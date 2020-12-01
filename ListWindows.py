#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# ListWindows: окна со списками сообщений.
# Пример 14.3 (Лутц Т2 стр.387)
"""
# ---------------------------------------------------------------------------- #
Реализация окон со списками сообщений на почтовом сервере и в локальных
файлах: по одному для каждого типа окон. Здесь использован прием
выделения общего программного кода для повторного использования: окна
со списками содержимого на сервере и в файлах являются специализированными
версиями класса PyMailCommon окон со списками; класс окна со списком почты
на сервере отображает свои операции на операции получения почты с сервера,
класс окна со списком почты в файле отображает свои операции на операции
с локальным файлом.

В ответ на действия пользователя окна со списками создают окна просмотра,
создания, ответа и пересылки писем. Окно со списком сообщений на сервере
играет роль главного окна и открывается при запуске сценарием верхнего
уровня; окна со списками сообщений в файлах открываются по требованию,
щелчком на кнопке "Open" в окне со списком сообщений на сервере или в файле.
Номера сообщений могут временно рассинхронизироваться с сервером, в случае
изменения содержимого почтового ящика входящих сообщений (вызывает полную
перезагрузку списка).

Изменения в этом модуле в версии 2.1:
- теперь проверяет синхронизацию номеров сообщений при удалении и загрузке
- добавляет в окна просмотра до N кнопок прямого доступа к вложениям
- загрузка из файлов выполняется в отдельном потоке, чтобы избежать задержек
  при загрузке больших файлов
- удаление отправленных сообщений из файла также выполняется в потоке,
  благодаря чему исчезла задержка в работе графического интерфейса

Что сделать:
- сохранение отправленных сообщений в файл до сих пор выполняется в главном
  потоке: это может вызывать короткие паузы в работе графического интерфейса,
  хотя это маловероятно - в отличие от загрузки и удаления,
  сохранение/отправка просто записывает сообщение в конец файла.
- реализация операций с локальными файлами, как с текстовыми файлами
  с разделителями в значительной степени является лишь прототипом:
  она загружает полные тексты сообщений целиком в память, что ограничивает
  возможный размер этих файлов; лучшее решение: использовать 2 DBM-файла
  с доступом по ключу - для заголовков и для полного текста сообщений,
  плюс список для отображения ключей в позиции; в такой реализации
  файлы с сообщениями превращаются в каталоги и становятся нечитаемыми
  для человка.
# ---------------------------------------------------------------------------- #
"""

from SharedNames import *									# глобальные объекты программы
from ViewWindows import ViewWindow, WriteWindow, ReplyWindow, ForwardWindow

# ---------------------------------------------------------------------------- #
# основной фрейм - общая структура списков с сообщениями на сервере и в файлах
# ---------------------------------------------------------------------------- #

# ANCHOR PyMailCommon
class PyMailCommon(mailtools.MailParser):
	"""
	абстрактный пакет виджетов с главным списком сообщений;
	смешивается с классами Tk, Toplevel или Frame окон верхнего уровня;
	должен специализироваться в подклассах с помощью метода actions()
	и других; создает окна просмотра и создания по требованию:
	они играют роль MailSenders;
	"""
	# атрибуты класса, совместно используемые всеми окнами со списками
	threadLoopStarted = False								# запускается первым окном
	queueChecksPerSecond = 20								# изменит, в зависимости нагрузки на процессор
	queueDelay = 1000 // queueChecksPerSecond				# минимальное число миллисекунд между событиями таймера
	queueBatch = 5											# максимальное число вызовов обработчиков на одно событие от таймера

	# все окна используют одни и те же диалоги: запоминают последний каталог
	openDialog = Open(title=appname + ': Open Mail File')
	saveDialog = SaveAs(title=appname + ': Append Mail File')

	# 3.0: чтобы избежать загрузки одного и того же сообщения в разных потоках
	beingFetched = set()

	def __init__(self):
		self.makeWidgets()									# нарисовать содержимое окна: список панель
		if not PyMailCommon.threadLoopStarted:
			# запустить цикл проверки завершения потоков
			# цикл событий от таймера, в котором производится вызов обработчиков из очереди
			# один цикл для всех окон: окна со списками с сервера и из файла,
			# окна просмотра могут выполнять операции в потоках;
			# self - экземпляр класса Тк, Toplevel или Frame: достаточно будет виджета любого типа;
			# 3.0/4Е: для увеличения скорости обработки увеличено количество вызываемых обработчиков
			# и количество событий в секунду: ~100x/sec;
			PyMailCommon.threadLoopStarted = True
			threadtools.threadChecker(self, self.queueDelay, self.queueBatch)

	def makeWidgets(self):
		# добавить флажок "All" внизу
		tools = Frame(self, relief=SUNKEN, bd=2, cursor='hand2')
		tools.pack(side=BOTTOM, fill=X)
		self.allModeVar = IntVar()
		chk = Checkbutton(tools, text='All')
		chk.config(variable=self.allModeVar, command=self.onCheckAll)
		chk.pack(side=RIGHT)

		# добавить кнопки на панель инструментов внизу
		for (title, callback) in self.actions():
			if not callback:
				sep = Label(tools, text=title)				# 3.0: разделитель растет с окном
				sep.pack(side=LEFT, expand=YES, fill=BOTH)
			else:
				Button(tools, text=title, command=callback).pack(side=LEFT)

		# добавить список с возможностью выбора нескольких записей и полосами прокрутки
		listwide = mailconfig.listWidth or 74				# 3.0: настройка начального размера
		listhigh = mailconfig.listHeight or 15				# ширина = символы, высота = строки
		mails    = Frame(self)
		vscroll  = Scrollbar(mails)
		hscroll  = Scrollbar(mails, orient='horizontal')
		fontsz   = (sys.platform[:3] == 'win' and 8) or 10	# по умолчанию
		listbg   = mailconfig.listbg or 'white'
		listfg   = mailconfig.listfg or 'black'
		listfont = mailconfig.listfont or ('courier', fontsz, 'normal')
		listbox  = Listbox(mails, bg=listbg, fg=listfg, font=listfont)
		listbox.config(selectmode=EXTENDED)
		listbox.config(width=listwide, height=listhigh)
		listbox.bind('<Double-1>', (lambda event: self.onViewRawMail()))

		# связать список и полосы прокрутки
		vscroll.config(command=listbox.yview, relief=SUNKEN)
		hscroll.config(command=listbox.xview, relief=SUNKEN)
		listbox.config(yscrollcommand=vscroll.set, relief=SUNKEN)
		listbox.config(xscrollcommand=hscroll.set)

		# присоединяется последним = усекается первым
		mails.pack(side=TOP, expand=YES, fill=BOTH)
		vscroll.pack(side=RIGHT, fill=BOTH)
		hscroll.pack(side=BOTTOM, fill=BOTH)
		listbox.pack(side=LEFT, expand=YES, fill=BOTH)
		self.listBox = listbox

# ---------------------------------------------------------------------------- #
#                              обработчики событий                             #
# ---------------------------------------------------------------------------- #

	def onCheckAll(self):
		# щелчок на флажке "All"
		if self.allModeVar.get():
			self.listBox.select_set(0, END)
		else:
			self.listBox.select_clear(0, END)

	def onViewRawMail(self):
		"""
		может вызываться из потока: просмотр выбранных сообщений -
		необработанный текст заголовков, тела
		"""
		msgnums = self.verifySelectedMsgs()
		if msgnums:
			self.getMessages(msgnums, after=lambda: self.contViewRaw(msgnums))

	def contViewRaw(self, msgnums, pyedit=True):			# необходим полный TextEditor?
		for msgnum in msgnums:								# может быть вложенное определение
			fulltext = self.getMessage(msgnum)				# полный текст - декодированный Юникод
			if not pyedit:
				# вывести в виждете scrolledtext
				from tkinter.scrolledtext import ScrolledText
				window = windows.QuietPopupWindow(appname, 'raw message viewer')
				browser = ScrolledText(window)
				browser.insert('0.0', fulltext)
				browser.pack(expand=YES, fill=BOTH)
			else:
				# в 3.0/4Е: более полноценный текстовый редактор PyEdit
				wintitle = ' - raw message text'
				browser = textEditor.TextEditorMainPopup(self, winTitle=wintitle)
				browser.update()
				browser.setAllText(fulltext)
				browser.clearModified()

	def onViewFormatMail(self):
		"""
		может вызываться из потока: просмотр отобранных сообщений -
		выводит форматированное отображение в отдельном окне; вызывается
		не из потока, если вызывается из списка содержимого файла или
		сообщения уже были загружены; действие after вызывается только если
		предварительное получение в getMessages возможно и было выполнено
		"""
		msgnums = self.verifySelectedMsgs()
		if msgnums:
			self.getMessages(msgnums, after=lambda: self.contViewFmt(msgnums))

	def contViewFmt(self, msgnums):
		"""
		завершение операции вывода окна просмотра: извлекает основной текст,
		выводит окно (окна) для отображения; если необходимо, извлекает
		простой текст из html, выполняет перенос строк; сообщения в формате
		html: выводит извлеченный текст, затем сохраняет во временном файле
		и открывает в веб-браузере; части сообщений могут также открываться
		вручную из окна просмотра с помощью кнопки Split (Разбить)
		или кнопок быстрого доступа к вложениями; в сообщении, состоящем
		из единственной части, иначе: часть должна открываться вручную
		кнопкой Split (Разбить) или кнопкой быстрого доступа к части;
		проверяет необходимость открытия html в mailconfig;

		3.0: для сообщений, содержащих только разметку html, основной текст
		здесь имеет тип str, но сохраняется он в двоичном режиме, чтобы
		обойти проблемы с кодировками; это необходимо, потому что
		значительная часть электронных писем в настоящее время
		отправляется в формате html; в первых версиях делалась попытка
		подобрать кодировку и N возможных (utf-8, latin-1, по умолчанию
		для платформы), но теперь тело сообщения получается и сохраняется
		в двоичном виде, чтобы минимизировать любые потери точности;
		если позднее часть будет открываться по требованию, она точно
		так же будет сохранена в файл в двоичном режиме;

		предупреждение: запускаемый веб-браузер не получает оригинальные
		заголовки письма: ему, вероятно, придется строить свои догадки
		о кодировке или вам придется явно сообщать ему о кодировке, если
		в разметке html отсутствуют собственные заголовки с информацией
		о кодировке (они принимают форму тегов <meta> в разделе <head>,
		если таковой имеется; здесь ничего не вставляется в разметку html,
		так как некоторые корректно оформленные части в формате html уже
		имеют все необходимое); IE, похоже, способен обработать большинство
		файлов html; кодирования частей html в utf-8 также может оказаться
		вполне достаточным: эта кодировка может с успехом применяться
		к большинству типов текста;
		"""
		for msgnum in msgnums:
			fulltext = self.getMessage(msgnum)				# 3.0: str для анализа
			self.trace('---contViewFmt->')
			self.trace(str(fulltext))
			message = self.parseMessage(fulltext)
			ctype, content = self.findMainText(message)		# 3.0: декодированный Юникод
			if ctype in ['text/html', 'text/xml']:			# 3.0: извлечь текст
				content = html2text.html2text(content)
			content = wraplines.wrapText1(content, mailconfig.wrapsz)
			ViewWindow(headermap   = message,
					   showtext    = content,
					   origmessage = message)				# 3.0: декодирует заголовки

			# единственная часть, content-type text/HTML (грубо, но верно!)
			if ctype == 'text/html':
				if ((not mailconfig.verifyHTMLTextOpen) or
					askyesno(appname, 'Open message text in browser?')):
					# 3.0: перед декодированием в Юникод преобразовать из формата MIME
					ctype, asbytes = self.findMainText(message, asStr=False)
					try:
						from tempfile import gettempdir		# или виджет Тк
						tempname = os.path.join(gettempdir(),
												'pymailgui.html')
						tmp = open(tempname, 'wb')
						# FIXME ???
						tmp.close()
						tmp.write(asbytes)
						webbrowser.open_new('file://' + tempname)
					except:
						showerror(appname, 'Cannot open in browser')

	def onWriteMail(self):
		"""
		окно составления нового письма на пустом месте, без получения других
		писем; здесь ничего не требуется цитировать, но следует добавить
		подпись и записать адрес отправителя в заголовок Bcc, если этот
		заголовок разрешен в mailconfig; значение для заголовка From
		в mailconfig может быть интернационализированным:
		окно просмотра декодирует его;
		"""
		starttext = '\n'									# использовать текст подписи
		if mailconfig.mysignature:
			starttext += '%s\n' % mailconfig.mysignature
		From = mailconfig.myaddress
		WriteWindow(starttext = starttext,					# 3.0: заполнить заголовок Bcc
					headermap = dict(From=From, Bcc=From))

	def onReplyMail(self):
		"""
		может вызываться из потока: создание ответа на выбранные письма
		"""
		msgnums = self.verifySelectedMsgs()
		if msgnums:
			self.getMessages(msgnums, after=lambda: self.contReply(msgnums))

	def contReply(self, msgnums):
		"""
		завершение операции составления ответа: отбрасывает вложения,
		цитирует текст оригинального сообщения с помощью символов '>',
		добавляет подпись; устанавливает начальные значения заголовков
		To/From, беря их из оригинального сообщения или из модуля
		с настройками; не использует значение оригинального заголовка То
		для From: может быть несколько адресов или название списка рассылки;
		заголовок То сохраняет формат имя + <адрес>, даже если в имени
		используется ','; для заголовка То используется значение
		оригинального заголовка From, игнорирует заголовок reply-to,
		если таковой имеется; 3.0: копия ответа по умолчанию также
		отправляется всем получателям оригинального письма;

		3.0: чтобы обеспечить возможность использования запятых
		в качестве разделителей адресов, теперь используются
		функции getaddresses/parseaddr, благодаря которым корректно
		обрабатываются запятые, присутствующие в компонентах имен адресов;
		в графическом интерфейсе адреса в заголовке также разделяются
		запятыми, мы копируем запятые при отображении заголовков
		и используем getaddresses для разделения адресов,
		когда это необходимо; почтовые серверы требуют, чтобы в качестве
		разделителей адресов использовался символ ',';
		больше не использует parseaddr для получения первой пары
		имя/адрес из результата, возвращаемого getadresses:
		используйте полное значение заголовка From для заголовка То;

		3.0: здесь предусматривается декодирование заголовка Subject,
		потому что необходимо получить его текст, но класс окна просмотра,
		являющийся суперклассом окна редактирования, выполняет декодирование
		всех отображаемых заголовков (дополнительное декодирование
		заголовка Subject является пустой операцией); при отправке все
		заголовки и имена в заголовках с адресами, содержащие символы
		вне диапазона ASCII, в графическом интерфейсе присутствуют
		в декодированном виде, но внутри пакета mailtools обрабатываются
		в кодированном виде; quoteOrigText также декодирует первоначальные
		значения заголовков, вставляемые в цитируемый текст, и окна
		со списками декодируют заголовки для отображения;
		"""
		self.trace('Enter to ListWindows.contReply')
		for msgnum in msgnums:
			fulltext = self.getMessage(msgnum)
			message = self.parseMessage(fulltext)			# при ошибке - объект ошибки
			maintext = self.formatQuotedMainText(message)	# то же для пересылки

			# заголовки From и То декодируются окном просмотра
			From = mailconfig.myaddress						# не оригинальный То
			To = message.get('From', '')					# 3.0: разделитель ','
			Cc = self.replyCopyTo(message)					# 3.0: всех получателей в сс?
			Subj = message.get('Subject', '(no subject)')
			Subj = self.decodeHeader(Subj)					# декодировать, чтобы получить str

			if Subj[:4].lower() != 're: ':					# 3.0: Объединить
				Subj = 'Re: ' + Subj
			ReplyWindow(starttext = maintext,
						headermap = dict(From=From, To=To, Cc=Cc, Subject=Subj, Bcc=From))

	def onFwdMail(self):
		"""
		может вызываться из потока: пересылка выбранных писем
		"""
		msgnums = self.verifySelectedMsgs()
		if msgnums:
			self.getMessages(msgnums, after=lambda: self.contFwd(msgnums))

	def contFwd(self, msgnums):
		"""
		завершение операции пересылки письма: отбрасывает вложения, цитирует
		текст оригинального сообщения с помощью символов '>', добавляет
		подпись; смотрите примечания по поводу заголовков в методах
		реализации операции составления ответа; класс окна просмотра,
		являющийся суперклассом, выполнит декодирование заголовка From;
		"""
		for msgnum in msgnums:
			fulltext = self.getMessage(msgnum)
			message = self.parseMessage(fulltext)
			maintext = self.formatQuotedMainText(message)	# то же для ответа

			# начальное значение From берется из настроек, а не из оригинального письма
			From = mailconfig.myaddress						# кодированный или нет
			Subj = message.get('Subject', '(no subject)')
			Subj = self.decodeHeader(Subj)					# 3.0: закодируется при отправке
			if Subj[:5].lower() != 'fwd: ':					# 3.0: объединить
				Subj = 'Fwd: ' + Subj
			ForwardWindow(starttext = maintext,
						  headermap = dict(From=From, Subject=Subj, Bcc=From))

	def onSaveMailFile(self):
		"""
		сохраняет выбранные письма в файл для просмотра без подключения
		к Интернету; запрещается, если в текущий момент выполняются
		операции загрузки/удаления с целевым файлом; также запрещаются
		методом getMessages, если self в текущий момент выполняет операции
		с другим файлом; метод contSave не поддерживает многопоточный
		режим выполнения: запрещает все остальные операции;
		"""
		msgnums = self.selectedMsgs()
		if not msgnums:
			showerror(appname, 'No message selected')
		else:
			# предупреждение: диалог предупреждает о перезаписи существующего файла
			filename = self.saveDialog.show()				# атрибут класса
			if filename:									# не проверять номера
				filename = os.path.abspath(filename)		# нормализовать / в \
				self.getMessages(msgnums, after=lambda: self.contSave(msgnums, filename))

	def contSave(self, msgnums, filename):
		"""
		проверяет возможность продолжения, после возможной загрузки
		сообщений с сервера
		"""
		if (filename in openSaveFiles.keys() and			# это файл просматривается ?
			openSaveFiles[filename].openFileBusy):			# операции загрузки/удаления ?
			showerror(appname, 'Target file busy - cannot save')
		else:
			try:											# предупреждение: не многопоточное
				fulltextlist = []							# 3.0: используем кодировку
				mailfile = open(filename, 'a', encoding=mailconfig.fetchEncoding)
				for msgnum in msgnums:						# < 1 сек для N сообщений
					fulltext = self.getMessage(msgnum)		# но сообщений может быть слишком много
					if fulltext[-1] != '\n': fulltext += '\n'
					mailfile.write(saveMailSeparator)
					mailfile.write(fulltext)
					fulltextlist.append(fulltext)
				mailfile.close()
			except:
				showerror(appname, 'Error during save')
				printStack(sys.exc_info())
			else:											# почему .keys(): EBIT (явное лучше неявного)
				if filename in openSaveFiles.keys():		# этот файл уже открыт?
					window = openSaveFiles[filename]		# обновить список, чтобы избежать повторного открытия
					window.addSavedMails(fulltextlist)
					# window.loadMailFileThread()			# это было очень медленно

	def onOpenMailFile(self, filename=None):
		"""
		обработка сохраненной почты без подключения к Интернету
		"""
		filename = filename or self.openDialog.show()		# общий атрибут класса
		if filename:
			filename = os.path.abspath(filename)			# полное имя файла
			if filename in openSaveFiles.keys():			# только 1 окно на файл
				openSaveFiles[filename].lift()				# поднять окно файла,
				showinfo(appname, 'File already open')		# иначе будут возникать ошибки после удаления
			else:
				from PyMailGui import PyMailFileWindow		# избежать дублирования
				popup = PyMailFileWindow(filename)			# новое окно со списком
				openSaveFiles[filename] = popup				# удаляется при закрытии
				popup.loadMailFileThread()					# загрузить в потоке

	def onDeleteMail(self):
		"""
		удаляет выбранные письма с сервера или из файла
		"""
		msgnums = self.selectedMsgs()						# подкласс fillIndex
		if not msgnums:										# всегда проверять
			showerror(appname, 'No message selected')
		else:
			if askyesno(appname, 'Verify delete %d mails?' % len(msgnums)):
				self.doDelete(msgnums)

# ---------------------------------------------------------------------------- #
#                            вспомогательные методы                            #
# ---------------------------------------------------------------------------- #

	def selectedMsgs(self):
		"""
		возвращает выбранные в списке сообщения
		"""
		selections = self.listBox.curselection()			# кортеж строк-чисел, 0..N-1
		return [int(x)+1 for x in selections]				# преобразование в int, создает 1..N

	warningLimit = 15

	def verifySelectedMsgs(self):
		msgnums = self.selectedMsgs()
		if not msgnums:
			showerror(appname, 'No message selected')
		else:
			numselects = len(msgnums)
			if numselects > self.warningLimit:
				if not askyesno(appname, 'Open %d selections?' % numselects):
					msgnums = []
		return msgnums

	def fillIndex(self, maxhdrsize=25):
		"""
		заполняет запись в списке содержимым заголовков;
		3.0: декодирует заголовки в соответствии с email/mime/unicode, если необходимо;
		3.0: предупреждение: крупные символы из китайского алфавит могут нарушить выравнивание границ '|' колонок;
		"""
		hdrmaps = self.headersMaps()						# может быть пустым
		showhdrs = ('Subject', 'From', 'Date', 'To')		# заголовки по умолчанию
		if hasattr(mailconfig, 'listheaders'):				# заголовки в mailconfig
			showhdrs = mailconfig.listheaders or showhdrs
		addrhdrs = ('From', 'To', 'Cc', 'Bcc')				# 3.0: декодируются особо

		# вычислить максимальный размер поля
		maxsize = {}
		for key in showhdrs:
			allLens = []									# слишком большой для списка
			for msg in hdrmaps:
				keyval = msg.get(key, ' ')
				if key not in addrhdrs:
					allLens.append(len(self.decodeHeader(keyval)))
				else:
					allLens.append(len(self.decodeAddrHeader(keyval)))
			if not allLens: allLens[1]
			maxsize[key] = min(maxhdrsize, max(allLens))

		# заполнить окно списка полями фиксированной ширины с выравниванием по левому краю
		self.listBox.delete(0, END)							# наличие нескольких частей отметить *
		for (ix, msg) in enumerate(hdrmaps):				# по заголовкам content-type
			msgtype = msg.get_content_maintype()			# нет метода is_multipart()
			msgline = (msgtype == 'multipart' and '*') or ' '
			msgline += '%03d' % (ix+1)
			for key in showhdrs:
				mysize = maxsize[key]
				if key not in addrhdrs:
					keytext = self.decodeHeader(msg.get(key, ' '))
				else:
					keytext = self.decodeAddrHeader(msg.get(key, ' '))
				msgline += ' | %-*s' % (mysize, keytext[:mysize])
			msgline += '| %.1fK' % (self.mailSize(ix+1) / 1024)
			self.listBox.insert(END, msgline)
		self.listBox.see(END)								# самое свежее сообщение в последней строке

	def replyCopyTo(self, message):
		"""
		3.0: при создании ответа все получатели оригинального письма
		копируются из заголовка То и Сс в заголовок Сс ответа после
		удаления дубликатов, и определяется новый отправитель;
		могло бы потребоваться декодировать интернационализированные адреса,
		но окно просмотра уже декодирует их для отображения (при отправке
		они повторно кодируются). Фильтрация уникальных значений здесь
		обеспечивается множеством в любом случае, если предполагается,
		что интернационализированный адрес отправителя в mailconfig будет
		представлен в кодированной форме (иначе здесь он не будет
		удаляться); здесь допускаются пустые заголовки То и Сс: split
		вернет пустой список;
		"""
		if not mailconfig.repliesCopyToAll:
			# ответить только отправителю
			Cc = ''
		else:
			# скопировать всех получателей оригинального письма (3.0)
			allRecipients = (self.splitAddresses(message.get('To', '')) +
							 self.splitAddresses(message.get('Cc', '')))
			uniqueOthers = set(allRecipients) - set([mailconfig.myaddress])
			Cc = ', '.join(uniqueOthers)
		return Cc or '?'

	def formatQuotedMainText(self, message):
		"""
		3.0: общий программный код, используемый операциями создания ответа
		и пересылки: получает декодированный текст, извлекает текст из html,
		переносит длинные строки, добавляет символы цитирования '>'
		"""
		mtype, maintext = self.findMainText(message)		# 3.0: декодированная строка str
		if mtype in ['text/html', 'text/xml']:				# 3.0: простой текст
			maintext = html2text.html2text(maintext)
		maintext = wraplines.wrapText1(maintext, mailconfig.wrapsz-2)		# 2 = '>'
		maintext = self.quoteOrigText(maintext, message)	# добавить заголовoк и '>'
		if mailconfig.mysignature:
			maintext = ('\n%s\n' % mailconfig.mysignature) + maintext
		return maintext

	def quoteOrigText(self, maintext, message):
		"""
		3.0: здесь необходимо декодировать все интернационализированные
		заголовки, иначе они будут отображаться в цитируемом тексте
		в кодированой форме email+MIME; decodeAddrHeader обрабатывает
		один адрес или список адресов, разделенных запятыми; при отправке
		это может вызвать кодирование полного текста сообщения, но основной
		текст уже в полностью декодированной форме: мог быть закодирован
		в любой кодировке;
		"""
		quoted = '\n-----Original Message-----\n'
		for hdr in ('From', 'To', 'Subject', 'Date'):
			rawhdr = message.get(hdr, '?')
			if hdr not in ('From', 'To'):
				dechdr = self.decodeHeader(rawhdr)				# весь заголовок
			else:
				dechdr = self.decodeAddrHeader(rawhdr)			# только имя в адресе
			quoted += '%s: %s\n' % (hdr, dechdr)
		quoted += '\n' + maintext
		quoted = '\n' + quoted.replace('\n', '\n> ')
		return quoted

# ---------------------------------------------------------------------------- #
#                             требуются подклассам                             #
# ---------------------------------------------------------------------------- #

	# используются операциями просмотра, сохранения,
	# создания ответа, пересылки
	def getMessages(self, msgnums, after):						# переопределить, если имеется кэш
		after()													# проверка потока

	# плюс okayQuit ? и все уникальные операции
	def getMessage(self, msgnum): assert False					# используется многими: полный текст
	def headersMaps(self): assert False							# fillIndex: список заголовков
	def mailSize(self, msgnum): assert False					# fillIndex: размер msgnum
	def doDelete(self): assert False							# onDeleteMail: кнопка Delete

# ---------------------------------------------------------------------------- #
# главное окно - при просмотре сообщений в локальном файле
# (или в файле отправленных сообщений)
# ---------------------------------------------------------------------------- #

# ANCHOR PyMailFile
class PyMailFile(PyMailCommon):
	"""
	специализирует PyMailCommon для просмотра содержимого файла
	с сохраненной почтой; смешивается с классами Tk, Toplevel или Frame,
	добавляет окно списка; отображает операции загрузки, получения,
	удаления на операции с локальным текстовым файлом; операции
	открытия больших файлов и удаления писем здесь выполняются в потоках;

	операции сохранения и отправки выполняются в главном потоке, потому что
	вызывают лишь добавление в конец файла; сохранение запрещается, если
	исходный или целевой файл в текущий момент используются операциями
	загрузки/удаления; операция сохранения запрещает загрузку, удаление,
	сохранение только потому, что она не выполняется в параллельном потоке
	(блокирует графический интерфейс);

	Что сделать: может потребоваться использовать потоки выполнения
	и блокировки файлов на уровне операционной системы, если сохранение
	когда-либо будет выполняться в потоках; потоки выполнения: операции
	сохранения могли бы запрещать другие операции сохранения в этот же
	файл с помощью openFileBusy, но файл может открываться не только
	в графическом интерфейсе; блокировок файлов недостаточно, потому что
	графический интерфейс обновляется;
	Что сделать: операция добавления в конец файла с сохраненными
	почтовыми сообщениями может потребовать использования блокировок
	на уровне операционной системы: в данной реализации при попытке
	выполнить отправку во время операций загрузки/удаления пользователь
	увидит диалог с сообщением об ошибке;

	3.0: сейчас файлы с сохраненными почтовыми сообщениями являются
	текстовыми, их кодировка определяется настройками в модуле mailconfig;
	вероятно, это не гарантирует поддержку в самом худшем случае
	применения необычных кодировок или смешивания разных кодировок,
	но в большинстве своем полный текст почтовых сообщений состоит только
	из смиволов ascii, и пакет email в Python 3.1 еще содержит ошибки;
	"""
	def actions(self):
		return [
			('Open', self.onOpenMailFile),
			('Write', self.onWriteMail),
			(' ', None),									# 3.0: разделители
			('View', self.onViewFormatMail),
			('Reply', self.onReplyMail),
			('Fwd', self.onFwdMail),
			('Save', self.onSaveMailFile),
			('Delete', self.onDeleteMail),
			(' ', None),
			('Quit', self.quit)
		]

	def __init__(self, filename):
		"""
		вызывающий: выполняет затем loadMailFileThread
		"""
		PyMailCommon.__init__(self)
		self.filename = filename
		self.openFileBusy = threadtools.ThreadCounter()		# 1 файл - 1 окно

	def loadMailFileThread(self):
		"""
		загружает или повторно загружает файл и обновляет окно со списком
		содержимого; вызывается операциями открытия, на этапе запуска
		программы и, возможно, операциями отправки, если файл
		с отправленными сообщениями открыт в настоящий момент;
		в файле всегда присутствует первый фиктивный элемент
		после разбиения текста;
		альтернатива: [self.parseHeaders(m) for m in self.msglist];
		можно было бы выводить диалог с информацией о ходе выполнения
		операции, но загрузка небольших файлов выполняется очень быстро;

		2.1: теперь поддерживает многопоточную модель выполнения - загрузка
		небольших файлов выполняется < 1 сек., но загрузка очень больших
		файлов может вызывать задержки в работе графического интерфейса;
		операция сохранения теперь использует addSavedMails для добавления
		списков сообщений, чтобы повысить скорость, но это относится
		к повторной загрузке; все еще вызывается операцией отправки, просто
		потому что текст сообщения недоступен - требуется провести
		рефакторинг; удаление также производится в потоке выполнения:
		предусмотрено предотвращение возможности перекрытия операций
		открытия и удаления;
		"""
		if self.openFileBusy:
			# не допускать параллельное выполнение операций открытия/удаления
			errmsg = 'Cannot load, file is busy:\n"%s"' % self.filename
			showerror(appname, errmsg)
		else:
			# self.listBox.insert(END, 'loading...')		# вызывает ошибку при щелчке
			savetitle = self.title()						# устанавливается классом окна
			self.title(appname + ' - ' + 'Loading...')
			self.openFileBusy.incr()
			threadtools.startThread(
				action  = self.loadMailFile,
				args    = (),
				context = (savetitle,),
				onExit  = self.onLoadMailFileExit,
				onFail  = self.onLoadMailFileFail
			)

	def loadMailFile(self):
		"""
		выполняется в потоке, оставляя графический интерфейс активным
		операции открытия, чтения и механизм анализа могут возбуждать
		исключения: перехватывается в утилитах работы с потоками
		"""
		file = open(self.filename, 'r', encoding=mailconfig.fetchEncoding)
		allmsgs = file.read()
		self.msglist = allmsgs.split(saveMailSeparator)[1:]			# полный текст
		self.hdrlist = list(map(self.parseHeaders, self.msglist))	# объекты сообщений

	def onLoadMailFileExit(self, savetitle):
		"""
		успешная загрузка в потоке
		"""
		self.title(savetitle)										# записать имя файла в заголовк окна
		self.fillIndex()											# обновить графический интерфейс: выполняется в главном потоке
		self.lift()													# поднять окно
		self.openFileBusy.decr()

	def onLoadMailFileFail(self, exc_info, savetitle):
		"""
		исключение в потоке
		"""
		showerror(appname, 'Error opening "%s"\n%s\n%s' % ((self.filename,) + exc_info[:2]))
		printStack(exc_info)
		self.destroy()												# всегда закрывать окно?
		self.openFileBusy.decr()									# не требуется при уничтожении окна

	def addSavedMails(self, fulltextlist):
		"""
		оптимизация: добавляет вновь сохраняемые сообщения в окна
		со списками содержимого, загруженного из файлов; в прошлом
		при сохранении выполнялась перезагрузка всего файла
		вызовом loadMailThread - это медленно;
		должен вызываться только в главном потоке выполнения:
		обновляет графический интерфейс; операция отправки по-прежнему
		вызывает перезагрузку файла с отправленными сообщениями, если он
		открыт: отсутствует текст сообщения;
		"""
		self.msglist.extend(fulltextlist)
		self.hdrlist.extend(map(self.parseHeaders, fulltextlist))
		self.fillIndex()
		self.lift()

	def doDelete(self, msgnums):
		"""
		бесхитростная реализация, но ее вполне достаточно: перезаписывает
		в файл все неудаленные сообщения; недостаточно просто удалить
		из self.msglist: изменяются индексы элементов списка;
		Py2.3 enumerate(L) - то же самое, что zip(range(len(L)), L)

		2.1: теперь поддерживает многопoточную модель выполнения, иначе
		может вызывать паузы в работе графического интерфейса при работе
		с очень большими файлами
		"""
		if self.openFileBusy:
			# не допускать параллельное выполнение операций
			errmsg = 'Cannot delete, file is busy:\n"%s"' % self.filename
			showerror(appname, errmsg)
		else:
			savetitle = self.title()
			self.title(appname + ' - ' + 'Deleting...')
			self.openFileBusy.incr()
			threadtools.startThread(
				action  = self.deleteMailFile,
				args    = (msgnums,),
				context = (savetitle,),
				onExit  = self.onDeleteMailFileExit,
				onFail  = self.onDeleteMailFileFail
			)

	def deleteMailFile(self, msgnums):
		"""
		выполняется в потоке, оставляя графический интерфейс открытым
		"""
		indexed = enumerate(self.msglist)
		keepers = [msg for (ix, msg) in indexed if ix+1 not in msgnums]
		allmsgs = saveMailSeparator.join([''] + keepers)
		file = open(self.filename, 'w', encoding=mailconfig.fetchEncoding)
		file.write(allmsgs)
		self.msglist = keepers
		self.hdrlist = list(map(self.parseHeaders, self.msglist))

	def onDeleteMailFileExit(self, savetitle):
		self.title(savetitle)
		self.fillIndex()											# обновляет графический интерфейс: выполняется в главном потоке
		self.lift()													# сбросить заголовок, поднять окно
		self.openFileBusy.decr()

	def onDeleteMailFileFail(self, exc_info, savetitle):
		showerror(appname, 'Error deleting "%s"\n%s\n%s' % ((self.filename,) + exc_info[:2]))
		printStack(exc_info)
		self.destroy()
		self.openFileBusy.decr()

	def getMessages(self, msgnums, after):
		"""
		используется операциями просмотра, сохранения, создания ответа,
		пересылки: потоки загрузки и удаления могут изменять
		списки сообщений и заголовков, поэтому следует
		запрещать выполнение других операций, безопасность которых
		зависит от них; этот метод реализует проверку для self:
		для операций сохранения также проверяется целевой файл;
		"""
		if self.openFileBusy:
			errmsg = 'Cannot fetch, file is busy:\n"%s"' % self.filename
			showerror(appname, errmsg)
		else:
			after()													# почта уже загружена

	def getMessage(self, msgnum):
		return self.msglist[msgnum-1]								# полный текст одного сообщения

	def headersMaps(self):
		return self.hdrlist											# объекты email.message.Message

	def mailSize(self, msgnum):
		return len(self.msglist[msgnum-1])

	def quit(self):
		"""
		не выполняет завершение в ходе обновления: следом вызывается fillIndex
		"""
		if self.openFileBusy:
			showerror(appname, 'Cannot quit during load or delete')
		else:
			if askyesno(appname, 'Verify Quit Window?'):
				# удалить файл из списка открытых файлов
				del openSaveFiles[self.filename]
				Toplevel.destroy(self)

# ---------------------------------------------------------------------------- #
#          главное окно - при просмотре сообщений на почтовом сервере          #
# ---------------------------------------------------------------------------- #

# ANCHOR PyMailServer
class PyMailServer(PyMailCommon):
	"""
	специализирует PyMailCommon для просмотра почты на сервере;
	смешивается с классaми Tk, Toplevel или Frame, добавляет окно со списком
	сообщений; отображает операции загрузки, получения, удаления на операции
	с почтовым ящиком на сервере; встраивает объект класса MessageCache,
	который является наследником класса MailFetcher из пакета mailtools;
	"""
	def actions(self):
		return [
			('Load', self.onLoadServer),
			('Open', self.onOpenMailFile),
			('Write', self.onWriteMail),
			(' ', None),
			('View', self.onViewFormatMail),
			('Reply', self.onReplyMail),
			('Fwd', self.onFwdMail),
			('Save', self.onSaveMailFile),
			('Delete', self.onDeleteMail),
			(' ', None),
			('Quit', self.quit)
		]

	def __init__(self):
		PyMailCommon.__init__(self)
		self.cache = messagecache.GuiMessageCache()					# встраивается, не наследуется
		# self.listBox.insert(END, 'Press Load to fetch mail')

	def makeWidgets(self):											# полоса вызова справки: только в главном окне
		self.addHelpBar()
		PyMailCommon.makeWidgets(self)

	def addHelpBar(self):
		msg = 'PyMailGUI - a Python/tkinter email client (help)'
		title = Button(self, text=msg)
		title.config(bg='steelblue', fg='white', relief=RIDGE)
		title.config(command=self.onShowHelp)
		title.pack(fill=X)

	def onShowHelp(self):
		"""
		загружает и отображает блок текстовых строк
		3.0: теперь использует также HTML и модуль webbrowser
		выбор между текстом, HTML или отображением и в том, и в другом
		формате определяется настройками в mailconfig всегда
		отображает справку: если оба параметра имеют значение,
		отображается справка в формате HTML
		"""
		if mailconfig.showHelpAsText:
			from PyMailGuiHelp import helptext
			popuputil.HelpPopup(appname, helptext, showsource=self.onShowMySource)

		if mailconfig.showHelpAsHTML or (not mailconfig.showHelpAsText):
			from PyMailGuiHelp import showHtmlHelp
			showHtmlHelp()											# 3.0: HTML-версия не предусматривает возможность
																	# вывести файлы с исходными текстами

	def onShowMySource(self, showAsMail=False):
		"""
		отображает файлы с исходными текстами плюс
		импортирует модули кое-где
		"""
		import PyMailGui, ListWindows, ViewWindows, SharedNames, textConfig
		from Tom2.ch13.mailtools import (mailSender, mailFetcher, mailParser)
		# FIXME ??? возможны проблемы с mailconfig
		mymods = (
			PyMailGui, ListWindows, ViewWindows, SharedNames,
			PyMailGuiHelp, popuputil, messagecache, wraplines, html2text,
			mailtools, mailFetcher, mailSender, mailParser,
			mailconfig, textConfig, threadtools, windows, textEditor
		)
		for mod in mymods:
			source = mod.__file__
			if source.endswith('.pyc'):
				source = source[:-4] + '.py'						# предполагается присутствие файлов .py в том же каталоге
			if showAsMail:
				# не очень элегантно...
				code = open(source).read()							# 3.0: кодировка для платформы
				user = mailconfig.myaddress
				hdrmap = {'From': appname, 'To': user, 'Subject': mod.__name__}
				ViewWindow( showtext = code,
							headermap = hdrmap,
							origmessage = email.message.Message())
			else:
				# более удобный текстовый редактор PyEdit
				# 4E: предполагается, что текст в кодировке UTF8
				# (иначе PyEdit может запросить кодировку!)
				wintitle = ' - ' + mod.__name__
				textEditor.TextEditorMainPopup(self, source, wintitle, 'utf-8')

	def onLoadServer(self, forceReload=False):
		"""
		может вызываться в потоках: загружает или повторно загружает
		списoк заголовков по требованию; операции Exit, Fail, Progress
		вызываются методом threadChecker посредством очереди
		в обработчике after; загрузка может перекрываться
		во времени с отправкой, но запрещает все остальные операции;
		можно было бы выполнять одновременно с loadingMsgs,
		но может изменять кэш сообщений; в случае ошибки операций
		удаления/синхронизации принудительно вызывается forceReload,
		иначе загружает только заголовки вновь прибывших сообщений;
		2.1: cache.loadHeaders можно использовать для быстрой проверки
		синхронизации номеров сообщений с сервером, когда загружаются
		только заголовки вновь прибывших сообщений;
		"""
		if loadingHdrsBusy or deletingBusy or loadingMsgsBusy:
			showerror(appname, 'Cannot load headers during load or delete')
		else:
			loadingHdrsBusy.incr()
			self.cache.setPopPassword(appname)						# не обновлять графический интерфейс в потоке!
			popup = popuputil.BusyBoxNowait(appname, 'Loading message headers')
			threadtools.startThread(
				action = self.cache.loadHeaders,
				args = (forceReload,),
				context = (popup,),
				onExit = self.onLoadHdrsExit,
				onFail = self.onLoadHdrsFail,
				onProgress = self.onLoadHdrsProgress
			)

	def onLoadHdrsExit(self, popup):
		self.fillIndex()
		popup.quit()
		self.lift()
		loadingHdrsBusy.decr()										# разрешить выполнение других операций

	def onLoadHdrsFail(self, exc_info, popup):
		popup.quit()
		showerror(appname, 'Load failed: \n%s\n%s' % exc_info[:2])
		printStack(exc_info)
		loadingHdrsBusy.decr()
		if exc_info[0] == mailtools.MessageSynchError:				# синхронизировать
			self.onLoadServer(forceReload=True)						# новый поток:перезагрузить
		else:
			self.cache.popPassword = None							# заставить ввести в следующий раз

	def onLoadHdrsProgress(self, i, n, popup):
		popup.changeText('%d of %d' % (i, n))

	def doDelete(self, msgnumlist):
		"""
		может вызываться в потоках: теперь удаляет почту
		на сервере - изменяет номера сообщений;
		может перекрываться во времени только с операцией
		отправки, запрещает все операции, кроме отправки;
		2.1: cache.deleteMessages теперь проверяет результат команды ТОР,
		чтобы проверить соответствие выбранных сообщений на случай
		рассинхронизации номеров сообщений с сервером: это возможно в случае
		удаления почты другим клиентом или в результате автоматического
		удаления сообщений сервером - в случае ошибки загрузки некоторые
		провайдеры могут перемещать почту из папки входящих сообщений
		в папку недоставленных;
		"""
		if loadingHdrsBusy or deletingBusy or loadingMsgsBusy:
			showerror(appname, 'Cannot delete during load or delete')
		else:
			deletingBusy.incr()
			popup = popuputil.BusyBoxNowait(appname, 'Deleting selected mails')
			threadtools.startThread(
				action  = self.cache.deleteMessages,
				args    = (msgnumlist,),
				context = (popup,),
				onExit  = self.onDeleteExit,
				onFail  = self.onDeleteFail,
				onProgress = self.onDeleteProgress
			)

	def onDeleteExit(self, popup):
		self.fillIndex()											# не требуется повторно загружать с сервера
		popup.quit()												# заполнить оглавление обновленными данными из кэша
		self.lift()													# поднять окно с оглавлением, освободить блокировку
		deletingBusy.decr()

	def onDeleteFail(self, exc_info, popup):
		popup.quit()
		showerror(appname, 'Delete failed: \n%s\n%s' % exc_info[:2])
		printStack(exc_info)										# ошибка удаления
		deletingBusy.decr()											# или проверки синхронизации
		self.onLoadServer(forceReload=True)							# новый поток: номера изменились

	def onDeleteProgress(self, i, n, popup):
		popup.changeText('%d of %d' % (i, n))

	def getMessages(self, msgnums, after):
		"""
		может вызываться в потоках: загружает все выбранные сообщения в кеш;
		используется операциями сохранения, просмотра, создания ответа
		и пересылки для предварительного заполнения кэша; может
		перекрываться во времени с другими операциями загрузки сообщений
		и отправки, запрещает выполнение операции удаления
		и загрузки заголовков; действие "after" выполняется, только если
		получение сообщений разрешено и было выполнено успешно;
		2.1: cache.getMessages проверяет синхронизацию оглавления
		с сервером, но здесь проверка выполняется только
		при необходимости взаимодействия с сервером,
		когда требуемые сообщения отсутствуют в кэше;

		3.0: смотрите примечания к messagecache: теперь предотвращаются
		попытки загрузить сообщения, которые в настоящий момент уже
		загружаются, если пользователь щелкнет мышью, чтобы повторно
		запустить операцию, когда она уже выполняется;
		если какое-либо сообщение из числа выбранных уже загружается
		другим запросом, необходимо запретить загрузку всего пакета
		сообщений toLoad; иначе необходимо ждать завершения N других
		операций загрузки; операции загрузки по-прежнему могут
		перекрываться во времени fetches при условии,
		что их ничто не объединяет;
		"""
		if loadingHdrsBusy or deletingBusy:
			showerror(appname, 'Cannot fetch message during load or delete')
		else:
			toLoad = [num for num in msgnums if not self.cache.isLoaded(num)]
			if not toLoad:
				after()												# все уже загружено
				return												# обработать сейчас, не ждать диалога
			else:
				if set(toLoad) & self.beingFetched:					# 3.0: хоть одно загружено?
					showerror(appname, 'Cannot fetch any message being fetched')
				else:
					self.beingFetched |= set(toLoad)
					loadingMsgsBusy.incr()
					from popuputil import BusyBoxNowait
					popup = BusyBoxNowait(appname, 'Fetching message contents')
					threadtools.startThread(
						action     = self.cache.getMessages,
						args       = (toLoad,),
						context    = (after, popup, toLoad),
						onExit     = self.onLoadMsgsExit,
						onFail     = self.onLoadMsgsFail,
						onProgress = self.onLoadMsgsProgress
					)

	def onLoadMsgsExit(self, after, popup, toLoad):
		self.beingFetched -= set(toLoad)
		popup.quit()
		after()
		loadingMsgsBusy.decr()										# разрешить другие операции после onExit

	def onLoadMsgsFail(self, exc_info, after, popup, toLoad):
		self.beingFetched -= set(toLoad)
		popup.quit()
		showerror(appname, 'Fetch failed: \n%s\n%s' % exc_info[:2])
		printStack(exc_info)
		loadingMsgsBusy.decr()
		if exc_info[0] == mailtools.MessageSynchError:				# синхронизация с сервером
			self.onLoadServer(forceReload=True)						# новый поток: перезагрузить

	def onLoadMsgsProgress(self, i, n, after, popup, toLoad):
		popup.changeText('%d of %d' % (i, n))

	def getMessage(self, msgnum):
		return self.cache.getMessage(msgnum)						# полный текст

	def headersMaps(self):
		"""
		список объектов email.message.Message, в 3.х требуется вызвать
		функцию list() при использовании map()
		возвращает [self.parseHeaders(h) for h in self.cache.allHdrs()]
		"""
		return list(map(self.parseHeaders, self.cache.allHdrs()))

	def mailSize(self, msgnum):
		return self.cache.getSize(msgnum)
# FIXME okayToQuit - правильное название или okayQuit было?
	def okayToQuit(self):
		# есть хоть один действующий поток?
		filesbusy = [win for win in openSaveFiles.values() if win.openFileBusy]
		busy = loadingHdrsBusy or deletingBusy or sendingBusy or loadingMsgsBusy
		busy = busy or filesbusy
		return not busy