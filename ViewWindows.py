#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# ViewWindows: окна просмотра сообщений.
# Пример 14.4 (Лутц Т2 стр.409)
"""
# ---------------------------------------------------------------------------- #
Реализация окон просмотра сообщения, создания нового, ответа и пересылки:
каждому типу соответствует свой класс. Здесь применяется прием выделения
общего программного кода для многократного использования: класс окна
создания нового сообщения является подклассом окна просмотра, а окна ответа
и пересылки являются подклассами окна создания нового сообщения.
Окна, определяемые в этом файле, создаются окнами со списками, в ответ
на действие пользователя.

Предупреждение: действие кнопки 'Split', открывающей части/вложения,
недостаточно очевидно. 2.1: эта проблема была устранена добавлением кнопок
быстрого доступа к вложениям.
Новое в версии 3.0: для размещения полей заголовков вместо фреймов кнопок
задействован менеджер компоновки grid(), одинаково хорошо действующий
на всех платформах.
Новое в версии 3.0: добавлена поддержка кодировок Юникода для основного
текста сообщения + текстовых вложений при передаче.
Новое в версии 3.0: PyEdit поддерживает произвольные кодировки Юникода
для просматриваемых частей сообщений.
Новое в версии 3.0: реализована поддержка кодировок Юникода и форматов MIME
для заголовков в отправляемых сообщениях.

Что сделать: можно было бы не выводить перед закрытием окна, если
текст сообщения не изменялся (как в PyEdit 2.0), но эти окна несколько
больше, чем просто редактор, и не определяют факт изменения заголовков,
Что сделать: возможно, следует сделать диалог выбора файла в окнах создания
новых сообщений глобальным для всей программы? (сейчас каждое окно создает
собственный диалог).
# ---------------------------------------------------------------------------- #
"""

from SharedNames import *									# объекты, глобальные для всей программы

# ---------------------------------------------------------------------------- #
# окно просмотра сообщения - также являюется суперклассом для окон создания
# нового сообщения, ответа и пересылки
# ---------------------------------------------------------------------------- #

# ANCHOR ViewWindow class
class ViewWindow(windows.PopupWindow, mailtools.MailParser):
	"""
	подкласс класса Toplevel с дополнительными методами и встроенным
	объектом TextEditor; наследует saveParts, partList
	из mailtools.MailParser; подмешивается в логику специализированных
	подклассов прямым наследованием
	"""
	# атрибуты класса
	modelabel = 'View'										# используется в заголовках окон

	# NOTE имя mailconfig используется из модуля SahredNames
	from mailconfig import okayToOpenParts					# открывать ли вложения?
	from mailconfig import verifyPartOpens					# выводить запрос перед открытием каждой части?
	from mailconfig import maxPartButtons					# максимальное число кнопок + '...'
	from mailconfig import skipTextOnHtmlPart				# 3.0: только в браузере, не использовать PyEdit?

	tempPartDir = 'TempParts'								# каталог для временного сохранения вложений

	# все окна просмотра используют один и тот же диалог: запоминается последний каталог
	partsDialog = Directory(title=appname + ': Select parts save directory')

	def __init__(self, headermap, showtext, origmessage=None):
		"""
		IN: карта заголовков - это origmessage или собственный словарь
		с заголовками (для операции создания нового письма);
		IN: showtext - основная текстовая часть сообщения: извлеченная
		из сообщения или любой другой текст;
		IN: origmessage - объект email.message.Message для просмотра
		"""
		windows.PopupWindow.__init__(self, appname, self.modelabel)
		self.origMessage = origmessage
		self.makeWidgets(headermap, showtext)

	def makeWidgets(self, headermap, showtext):
		"""
		добавляет поля заголовков, кнопки операций и доступа к вложениям,
		текстовый редактор
		3.0: предполагается, что в аргументе showtext передается
		декодированная строка Юникода str; она будет кодироваться
		при отправке или при сохрaнении
		"""
		actionsframe = self.makeHeaders(headermap)
		if self.origMessage and self.okayToOpenParts:
			self.makePartButtons()
		self.editor = textEditor.TextEditorComponentMinimal(self)
		myactions = self.actionButtons()
		for (label, callback) in myactions:
			b = Button(actionsframe, text=label, command=callback)
			b.config(bg='beige', relief=RIDGE, bd=2)
			b.pack(side=TOP, expand=YES, fill=BOTH)

		# тело текста, присоединяется последним = усекается первым
		self.editor.pack(side=BOTTOM)						# может быть несколько редакторов
		self.update()										# 3.0: иначе текстовый курсор встанет в строке
		self.editor.setAllText(showtext)					# каждый имеет собственное содержимое
		lines = len(showtext.splitlines())
		lines = min(lines + 3, mailconfig.viewheight or 20)
		self.editor.setHeight(lines)						# иначе высота = 24, ширина = 80
		self.editor.setWidth(80)							# или из textConfig редактора PyEdit
		if mailconfig.viewbg:								# цвета, шрифты - в mailconfig
			self.editor.setBg(mailconfig.viewbg)
		if mailconfig.viewfg:
			self.editor.setFg(mailconfig.viewfg)
		if mailconfig.viewfont:								# также через меню Tools редактора
			self.editor.setFont(mailconfig.viewfont)

	def makeHeaders(self, headermap):
		"""
		добавляет поля ввода заголовков, возвращает фрейм
		с кнопками операций;
		3.0: для создания рядов метка/поле ввода использует менеджер
		компоновки grid(), одинаково хорошо действующий на всех платформах;
		также можно было бы использовать менеджер компоновки pack()
		с фреймами рядов и метками фиксированной ширины;

		3.0: декодирование интернационализированых заголовков
		(и компонентов имен в заголовках с адресами электронной почты)
		выполняется здесь, если это необходимо, так как они добавляются
		в графический интерфейс; некоторые заголовки, возможно, уже были
		декодированы перед созданием окон ответа/пересылки, где требуется
		использовать декодированный текст, но лишнее декодирование здесь
		не вредит им и оно необходимо для других заголовков и случаев, таких
		как просмотр полученных сообщений; при отображении в графическом
		интерфейсе заголовки всегда находятся в декодированной форме
		и будут кодироваться внутри пакета mailtools при передаче, если они
		содержат символы за пределами диапазона ASCII (смотрите реализацию
		класса Write); декодирование интернационализированных заголовков
		также происходит в окне с оглавлением почты и при добавлении
		заголовков в цитируемый текст; текстовое содержимое в теле письма
		также декодируется перед отображением и кодируется перед передачей
		в другом месте в системе (окна со списками, класс WriteWindow);

		3.0: при создании окна редактирования вызывающий программный код
		записывает адрес отправителя в заголовок Bcc, который подхватывается
		здесь для удобства в типичных ситуациях, если этот заголовок
		разрешен в mailconfig; при создании окна ответа также заполняется
		заголовок Сс, если разрешен, уникальными адресами получателей
		оригинального письма, включая адрес в заголовке From;
		"""
		top = Frame(self)
		top.pack(side=TOP, fill=X)
		left = Frame(top)
		left.pack(side=LEFT, expand=NO, fill=BOTH)
		middle = Frame(top)
		middle.pack(side=LEFT, expand=YES, fill=X)

		# множество заголовков может быть расширено в mailconfig (Bcc и др.?)
		self.userHdrs = ()
		showhdrs = ('From', 'To', 'Cc', 'Subject')
		if hasattr(mailconfig, 'viewheaders') and mailconfig.viewheaders:
			self.userHdrs = mailconfig.viewheaders
			showhdrs += self.userHdrs
		addrhdrs = ('From', 'To', 'Cc', 'Bcc')				# 3.0: декодируются отдельно
		self.hdrFields = []
		for (i, header) in enumerate(showhdrs):
			lab = Label(middle, text=header+':', justify=LEFT)
			ent = Entry(middle)
			lab.grid(row=i, column=0, sticky=EW)
			ent.grid(row=i, column=1, sticky=EW)
			middle.rowconfigure(i, weight=1)
			hdrvalue = headermap.get(header, '?')			# может быть пустым
			# 3.0: если закодирован, декодировать с учетом emal+mime+юникод
			if header not in addrhdrs:
				hdrvalue = self.decodeHeader(hdrvalue)
			else:
				hdrvalue = self.decodeAddrHeader(hdrvalue)
			ent.insert('0', hdrvalue)
			self.hdrFields.append(ent)						# порядок имеет значение в onSend
		middle.columnconfigure(1, weight=1)
		# FIXME почему left ?
		return left

	def actionButtons(self):								# должны быть методами для доступа к self
		return [
			('Cancel', self.destroy),						# закрыть окно просмотра тихо
			('Parts', self.onParts),						# список частей или тело
			('Split', self.onSplit)
		]

	def makePartButtons(self):
		"""
		добавляет до N кнопок быстрого доступа к частям/вложениям;
		альтернатива кнопкам Parts/Split (2.1); это нормально,
		когда временный каталог совместно используется всеми операциями:
		файл вложения не сохраняется, пока позднее не будет выбран и открыт;
		partname=partname требуется в lambda-выражениях в Py2.4;
		предупреждение: можно было бы попробовать пропустить главную
		текстовую часть;
		"""
		def makeButton(parent, text, callback):
			link = Button(parent, text=text, command=callback, relief=SUNKEN)
			if mailconfig.partfg: link.config(fg=mailconfig.partfg)
			if mailconfig.partbg: link.config(bg=mailconfig.partbg)
			link.pack(side=LEFT, fill=X, expand=YES)

		parts = Frame(self)
		parts.pack(side=TOP, expand=NO, fill=X)
		for (count, partname) in enumerate(self.partsList(self.origMessage)):
			if count == self.maxPartButtons:
				makeButton(parts, '...', self.onSplit)
				break
			openpart = (lambda partname=partname: self.onOnePart(partname))
			makeButton(parts, partname, openpart)

	def onOnePart(self, partname):
		"""
		отыскивает часть, соответствующую кнопке, сохраняет ее и открывает;
		допускается открывать несколько сообщений: каждый раз сохранение
		производится заново; вероятно, мы могли бы здесь просто
		использовать веб-браузер;
		предупреждение: tempPartDir содержит путь относительно cwd -
		может быть любым каталогом;
		предупреждение: tempPartDir никогда не очищается: может занимать
		много места на диске, можно было бы использовать модуль tempfile
		(как при отображении главной текстовой части в формате HTML
		в методе onView класса окна со списком;)
		"""
		try:
			savedir = self.tempPartDir
			message = self.origMessage
			(contype, savepath) = self.saveOnePart(savedir, partname, message)
		except:
			showerror(appname, 'Error while writing part file')
			printStack(sys.exc_info())
		else:
			self.openParts([(contype, os.path.abspath(savepath))])

	def onParts(self):
		"""
		отображает содержимое части/вложения сообщения в отдельном окне;
		использует ту же схему именования файлов, что и операция Split;
		если сообщение содержит единственную часть, она является
		тектовым телом
		"""
		partnames = self.partsList(self.origMessage)
		msg = '\n'.join(['Message parts:\n'] + partnames)
		showinfo(appname, msg)

	def onSplit(self):
		"""
		выводит диалог выбора каталога и сохраняет туда все части/вложения;
		при желании мультимедийные части и HTML открываются
		в веб-браузере, текст - в TextEditor, а документы
		известных типов - в соответствующих программах Windows;
		можно было бы отображать части в окнах View, где имеется
		встроенный текстовый редактор с функцией сохранения,
		но большинство частей являются нечитаемым текстом;
		"""
		savedir = self.partsDialog.show()					# атрибут класса: предыдущий каталог
		if savedir:											# диалог tk выбора каталога, не файла
			try:
				partfiles = self.saveParts(savedir, self.origMessage)
			except:
				showerror(appname, 'Error while writing part files')
				printStack(sys.exc_info())
			else:
				if self.okayToOpenParts: self.openParts(partfiles)

	def askOpen(self, appname, prompt):
		if not self.verifyPartOpens:
			return True
		else:
			return askyesno(appname, prompt)

	def openParts(self, partfiles):
		"""
		автоматически открывает файлы известных и безопасных типов,
		но только после подтверждения пользователем; файлы других
		типов должны открываться вручную из каталога сохранения;
		к моменту вызова этого метода именованные части уже преобразованы
		из формата MIME и хранятся в двоичных файлах, однако текстовые
		файлы могут содержать текст в любой кодировке; редактору PyEdit
		требуется знать кодировку для декодирования, веб-браузеры могут
		пытаться сами определять кодировку или позволять сообщать ее им;

		предупреждение: не открывает вложения типа application/octet-stream,
		даже если имя файла имеет безопасное расширение, такое как .html;
		предупреждение: изображения/аудио/видео можно было бы открывать
		с помощью сценария playfile.py из этой книги; в случае ошибки
		средства просмотра текста: в Windows можно было бы также
		запускать Notepad (Блокнот) с помощью startfile;
		(в большинстве случаев также можно было бы использовать
		модуль webbrowser, однако специализированный
		инструмент всегда лучше универсального);
		"""
		def textPartEncoding(fullfilename):
			"""
			3.0: отображает имя файла текстовой части в содержимое
			параметра charset в заголовке content-type для данной части
			сообщения Message, которое затем передается конструктору PyEdit,
			чтобы обеспечить корректное отображение текста; для текстовых
			частей можно было бы возвращать параметр charset вместе
			с content-type из mailtools, однако проще обрабатывать эту
			ситуацию как особый случай здесь;

			содержимое части сохрaняется пакетом mailtools в двоичном
			режиме, чтобы избежать проблем с кодировками, но здесь
			отсутствует прямой доступ к оригинальной части сообщения;
			необходимо выполнить это отображение, чтобы получить
			имя кодировки, если оно присутствует;
			редактор PyEdit в 4 издании теперь позволяет явно указывать
			кодировку открываемого файла и определяет кодировку
			при сохранении; смотрите главу 11, где описываются особенности
			поведения PyEdit: он запрашивает кодировку у пользователя,
			если кодировка не указана или оказывается неприменимой;
			предупреждение: перейти на mailtools.mailParser в PyMailCGI,
			чтобы повторно использовать для тега <meta>?
			"""
			partname = os.path.basename(fullfilename)
			for (filename, contype, part) in self.walkNamedParts(self.origMessage):
				if filename == partname:
					return part.get_content_charset()		# None, если нет в заголовках
			assert False, 'Text part not found'				# никогда не должна выполняться

		for (contype, fullfilename) in partfiles:
			maintype = contype.split('/')[0]				# левая часть
			extension = os.path.splitext(fullfilename)[1]	# не [-4:]
			basename = os.path.basename(fullfilename)		# отбросить путь

			# текст в формате HTML и XML, веб-страницы, некоторые мультимедийные файлы
			if contype in ['text/html', 'text/xml']:
				browserOpened = False
				if self.askOpen(appname, 'Open "%s" in browser?' % basename):
					try:
						webbrowser.open_new('file://' + fullfilename)
						browserOpened = True
					except:
						showerror(appname, 'Browser failed: trying editor')
				if not browserOpened or not self.skipTextOnHtmlPart:
					try:
						# попробовать передать редактору PyEdit имя кодировки
						encoding = textPartEncoding(fullfilename)
						textEditor.TextEditorMainPopup(parent = self,
													   winTitle = ' - %s email part' % (encoding or '?'),
													   loadFirst = fullfilename,
													   loadEncode = encoding)
					except:
						showerror(appname, 'Error opening text viewer')

			# text/plain, text/x-python и др.; 4Е: кодировка может не подойти
			elif maintype == 'text':
				if self.askOpen(appname, 'Open text part "%s"?' % basename):
					try:
						encoding = textPartEncoding(fullfilename)
						textEditor.TextEditorMainPopup(parent = self,
													   winTitle = ' - %s email part' % (encoding or '?'),
													   loadFirst = fullfilename,
													   loadEncode = encoding)
					except:
						showerror(appname, 'Error opening text viewer')

			# мультимедийные файлы: Windows открывает mediaplayer, imageviewer и так далее
			elif maintype in ['image', 'audio', 'video']:
				if self.askOpen(appname, 'Open media part "%s"?' % basename):
					try:
						webbrowser.open_new('file://' + fullfilename)
					except:
						showerror(appname, 'Error opening browser')

			# типичные документы Windows: Word, Excel, Adobe, фрхивы и др.
			elif (sys.platform[:3] == 'win' and
				  maintype == 'application' and
				  extension in ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.zip', '.tar', '.wmv']):
				if self.askOpen(appname, 'Open part "%s"?' % basename):
					os.startfile(fullfilename)
			else:											# пропустить
				msg = 'Cannot open part: "%s"\nOpen manually in: "%s"'
				msg = msg % (basename, os.path.dirname(fullfilename))
				showinfo(appname, msg)

# ---------------------------------------------------------------------------- #
# окна редактирования сообщений - операции создания нового сообщения,
# ответа и пересылки
# ---------------------------------------------------------------------------- #

if mailconfig.smtpuser:										# пользователь определен в mailconfig?
	MailSenderClass = mailtools.MailSenderAuth				# требуется имя/пароль
else:
	MailSenderClass = mailtools.MailSender

# ANCHOR WriteWindow class
class WriteWindow(ViewWindow, MailSenderClass):
	"""
	специализирует окно просмотра для составления нового сообщения
	наследует sendMessage из mailtools.MailSender
	"""
	modelabel = 'Write'

	def __init__(self, headermap, starttext):
		ViewWindow.__init__(self, headermap, starttext)
		MailSenderClass.__init__(self)
		self.attaches = []									# каждое окно имеет свой диалог открытия
		self.openDialog = None								# диалог запоминает последний каталог

	def actionButtons(self):								# должны быть методами для доступа к self
		return [
			('Cancel', self.quit),
			('Parts', self.onParts),						# PopupWindow проверяет отмену
			('Attach', self.onAttach),
			('Send', self.onSend)							# 4E: без отступов, по центру
		]

	def onParts(self):
		"""
		предупреждение: удаление в настоящее время не поддерживается
		"""
		if not self.attaches:
			showinfo(appname, 'Nothing attached')
		else:
			msg = '\n'.join(['Already attached:\n'] + self.attaches)
			showinfo(appname, msg)

	def onAttach(self):
		"""
		вкладывает файл в письмо: имя, добавляемое здесь, будет добавлено
		как часть в операции Send, внутри пакета mailtools;
		4E: имя кодировки Юникода можно было бы запрашивать здесь,
		а не при отправке
		"""
		if not self.openDialog:
			self.openDialog = Open(title=appname + ': Select Attachment File')
		filename = self.openDialog.show()					# запомнить каталог
		if filename:
			self.attaches.append(filename)					# для открытия в методе отправки

	def resolveUnicodeEncodings(self):
		"""
		3.0/4E: в качестве подготовки к отправке определяет кодировку Юникода
		для текстовых частей: для основной текстовой части и для любых
		текстовых вложений; кодировка для основной текстовой части может
		быть уже известна, если это ответ или пересылка, но она не известна
		при создании нового письма, к тому же в результате редактирования
		кодировка может измениться; модуль smtplib в 3.1 требует, чтобы
		полный текст отправляемого сообщения содержал только символы ASCII
		(если это str), поэтому так важно определить кодировку пpямо здесь;
		иначе будет возникать ошибка при попытке отправить
		ответ/пересылаемое письмо с текстом в кодировке UTF8, когда
		установлен параметр config=ascii, а текст содержит символы
		вне диапазона ASCII; пытается использовать настройки пользователя
		и выполнить ответ, а в случае неудачи возвращается к универсальной
		кодировке UTF8 как к последней возможности;
		"""
		def isTextKind(filename):
			contype, encoding = mimetypes.guess_type(filename)
			if contype is None or encoding is not None:
				return False								# не определяется, сжатый файл?
			maintype, subtype = contype.split('/', 1)		# проверить на text/?
			return maintype == 'text'

		# выяснить кодировку основного текста
		bodytextEncoding = mailconfig.mainTextEncoding
		if bodytextEncoding == None:
			asknow = askstring('PyMailGUI', 'Enter main text Unicode encoding name')
			bodytextEncoding = asknow or 'latin-1'			# или sys.getdefaultencoding?

		# последний шанс: использовать utf-8, если кодировку так и не удалось определить выше
		if bodytextEncoding != 'utf-8':
			try:
				bodytext = self.editor.getAllText()
				bodytext.encode(bodytextEncoding)
			except (UnicodeError, LookupError):
				bodytextEncoding = 'utf-8'

		# определить кодировки текстовых вложений
		attachesEncodings = []
		config = mailconfig.attachmentTextEncoding
		for filename in self.attaches:
			if not isTextKind(filename):
				attachesEncodings.append(None)				# не текст, не спрашивать
			elif config != None:
				attachesEncodings.append(config)			# для всех текстовых частей, если установлена
			else:
				prompt = 'Enter Unicode encoding name for %s' % filename
				asknow = askstring('PyMailGUI', prompt)
				attachesEncodings.append(asknow or 'latin-1')

			# последний шанс: использовать utf-8, если кодировку так и не удалось определить выше
			choice = attachesEncodings[-1]
			if choice != None and choice != 'utf-8':
				try:
					attachbytes = open(filename, 'rb').read()
					attachbytes.decode(choice)
				except (UnicodeError, LookupError, IOError):
					attachesEncodings[-1] = 'utf-8'
		return bodytextEncoding, attachesEncodings

	def onSend(self):
		"""
		может вызываться из потока: обработчик кнопки
		Send (Отправить) в окне редактирования;
		может перекрываться во времени с любыми другими потоками
		выполнения, не запрещает никаких операций, кроме завершения;
		обработчики Exit, Fail выполняются методом threadChecker
		посредством очереди в обработчике after;
		предупреждение: здесь не предусматривается вывод информации о ходе
		выполнения, потому что операция отправки почты является атомарной;
		допускается указывать несколько адресов получателей, разделенных ',';
		пакет mailtools решaет проблемы с кодировками, обрабатывает
		вложения, формирует строку даты и так далее; кроме того,
		пакет mailtools сохраняет текст отправленных сообщений в локальном файле

		3.0: теперь выполняется полный разбор заголовков То, Сс, Всс
		(в mailtools) вместо простого разбиения по символу-разделителю;
		вместо простых полей ввода можно было бы использовать
		многострочные виджеты; содержимое заголовков Всс добавляется
		на "конверт", а сам заголовок удаляется;

		3.0: кодировка Юникода для текстовых частей определяется здесь,
		потому что она может потребоваться для вывода подсказок
		в графическом интерфейсе; фактическое кодирование текстовых частей
		выполняется внутри пакета mailtools, если это необходимо;

		3.0: интернационализированные заголовки уже декодируются в полях
		ввода графического интерфейса; кодирование любых
		интернационализированных заголовков с смиволами вне диапазона ASCII
		выполняется не здесь, а в пакете mailtools, потому что эта операция
		не требуется для работы графического интерфейса;
		"""
		self.trace('Enter to WriteWindow.onSend')
		# определить кодировку для текстовых частей;
		bodytextEncoding, attachesEncodings = self.resolveUnicodeEncodings()

		# получить компоненты графического интерфейса;
		# 3.0: интернационализированные заголовки уже декодированы
		fieldvalues = [entry.get() for entry in self.hdrFields]
		From, To, Cc, Subj = fieldvalues[:4]
		extraHdrs = [('Cc', Cc), ('X-Mailer', appname + ' (Python)')]
		extraHdrs += list(zip(self.userHdrs, fieldvalues[4:]))
		bodytext = self.editor.getAllText()

		# разбить список получателей на адреса по ',', исправить пустые поля
		Tos = self.splitAddresses(To)
		for (ix, (name, value)) in enumerate(extraHdrs):
			if value:											# игнорировать, если ''
				if value == '?':								# ? не заменяется
					extraHdrs[ix] = (name, '')
				elif name.lower() in ['cc', 'bcc']:				# разбить по ','
					extraHdrs[ix] = (name, self.splitAddresses(value))

		# метод withdraw вызывается, чтобы предотвратить повторный запуск передачи во время передачи
		# предупреждение: не устраняет вероятность ошибки полностью - пользователь может восстановить
		# окно, если значок останется видимым
		self.withdraw()
		self.getPassword()										# если необходимо; не запускайте диалог в потоке!
		popup = popuputil.BusyBoxNowait(appname, 'Sending message')
		sendingBusy.incr()
		threadtools.startThread(
			action = self.sendMessage,
			args = (From, Tos, Subj, extraHdrs, bodytext, self.attaches,
					saveMailSeparator, bodytextEncoding, attachesEncodings),
			context = (popup,),
			onExit = self.onSendExit,
			onFail = self.onSendFail
		)

	def onSendExit(self, popup):
		"""
		стирает окно ожидания, стирает окно просмотра, уменьшает счетчик
		операций отправки; метод sendMessage автоматически сохраняет
		отправленное сообщение в локальном файле; нельзя использовать
		window.addSavedMails: текст почтового сообщения недоступен;
		"""
		popup.quit()
		self.destroy()
		sendingBusy.decr()

		# может быть \ при открытии, в mailconfig используется /
		sentname = os.path.abspath(mailconfig.sentmailfile)		# расширяет '.'
		if sentname in openSaveFiles.keys():					# файл открыт?
			window = openSaveFiles[sentname]					# обновить список
			window.loadMailFileThread()							# и подянть окно

	def onSendFail(self, exc_info, popup):
		"""
		выводит диалог с сообщением об ошибке, оставляет нетронутым окно
		с сообщением, чтобы имелась возможность сохранить или повторить
		попытку, перерисовывает фрейм
		"""
		popup.quit()
		self.deiconify()
		self.lift()
		showerror(appname, 'Send failed: \n%s\n%s' % exc_info[:2])
		printStack(exc_info)
		MailSenderClass.smtpPassword = None						# повторить попытку; 3.0/4Е: не в self
		sendingBusy.decr()

	def askSmtpPassword(self):
		"""
		получает пароль, если он необходим графическому интерфейсу,
		вызывается из главного потока выполнения;
		предупреждение: чтобы не возникла необходимость запрашивать пароль
		в потоке выполнения, если он не был введен в первый раз, выполняет
		цикл, пока пользователь не введет пароль; смотрите логику получения
		пароля доступа к POP-серверу, где приводится альтернативный вариант без цикла
		"""
		password = ''
		while not password:
			prompt = ('Password for %s on %s?' % (self.smtpUser, self.smtpServerName))
			password = popuputil.askPasswordWindow(appname, prompt)
		return password

# ANCHOR ReplyWindow class
class ReplyWindow(WriteWindow):
	"""
	специализированная версия окна создания сообщения для ответа
	текст и заголовки поставляются окном со списком
	"""
	modelabel = 'Reply'

# ANCHOR ForwardWindow class
class ForwardWindow(WriteWindow):
	"""
	специализированная версия окна создания сообщения для персылки
	текст и заголовки поставляются окном со списком
	"""
	modelabel = 'Forward'