#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# messagecache: менеджер кеша сообщений.
# Пример 14.5 (Лутц Т2 стр.421)
"""
# ---------------------------------------------------------------------------- #
управляет загрузкой сообщений с заголовками и контекстом, но не графическим
интерфейсом; подкласс класса MailFetcher, со списком загруженных заголовков
и сообщений; вызывающая программа сама должна заботиться о поддержке потоков
выполнения и графического интерфейса;

изменения в версии 3.0: использует кодировку для полного текста сообщений
из локального модуля mailconfig; декодирование выполняется глубоко в недрах
mailtools; после загрузки текст сообщения всегда возвращается в виде
строки Юникода str; это может измениться в будущих версиях Python/email:
подробности смотрите в главе 13;

изменения в версии 3.0: поддерживает новую особенность mailconfig.fetchlinit
в mailtools, которая может использоваться для ограничения максимального
числа самых свежих заголовков или сообщений (если не поддерживается команда
ТОР), загружмемых при каждом запросе на загрузку; обратите внимание, что эта
особенность является независимой от парамтера loadfrom, используемого здесь,
чтобы ограничить загрузку только самыми новыми сообщениями, хотя они
и используются одновременно: загружается не больше чем fetchlimit вновь
поступивших сообщений;

изменения в версии 3.0: есть вероятность, что пользователь запрсит загрузку
сообщения, которое в текущий момент уже загружается в параллельном потоке,
просто щелкнув на сообщении еще раз (операции загрузки сообщений, в отличие
от полной загрузки оглавления, могут перекрываться во времени с другими
операциями загрузки и отправки); в этом нет никакой опасности, но это может
привести к излишней и, возможно, параллельной загрузке одного и того же
письма, что бессмысленно и не нужно (если выбрать все сообщения в списке
и дважды нажать кнопку View, это может вызвать загрузку большинства
сообщений дважды!); в главном потоке графического интерфейса слежение
за загружаемыми сообщениями, чтобы такое перекрытие во времени не было
возможным: загружаемое сообщение препятствует выполнению операций загрузки
любых наборов сообщений, в которых оно присутствует, параллельная загрузка
непересекающихся множеств сообщений по-прежнему возможна;
# ---------------------------------------------------------------------------- #
"""

from Tom2.ch13 import mailtools
from popuputil import askPasswordWindow

class MessageInfo:
	"""
	элемент списка в кеше
	"""
	def __init__(self, hdrtext, size):
		self.hdrtext = hdrtext									# fulltext - кешированное сообщение
		self.fullsize = size									# hdrtext - только заголовки
		self.fulltext = None									# fulltext=hdrtext если не работает команда ТОР

class MessageCache(mailtools.MailFetcher):
	"""
	следит за уже загруженными заголовками и сообщениями;
	наследует от MailFetcher методы взаимодействия с сервером;
	может использоваться в других приложениях: ничего не знает о графическом
	интерфейсе или поддержке многопоточной модели выполнения;

	3.0: байты исходного полного текста сообщения декодируются в str, чтобы
	обеспечить возможность анализа пакетом email в Py3.1 и сохранения
	в файлах; использует настройки определения кодировок из локального
	модуля mailconfig; декодирование выполняется автоматически
	в пакете mailtools при получении;
	"""
	def __init__(self):
		mailtools.MailFetcher.__init__(self)					# 3.0: наследует fetchEncoding
		self.msglist = []										# 3.0: наследует fetchlimit

	def loadHeaders(self, forceReloads, progress=None):
		"""
		здесь обрабатываются три случая: первоначальная загрузка всего
		списка, загрузка вновь поступившей почты и принудительная
		перезагрузка после удаления; не получает повторно просмотренные
		сообщения, если список заголовков остался прежним или был дополнен;
		сохраняет кешированные сообщения после удаления, если операция
		удаления завершилась успешно;
		2.1: выполняет быструю проверку синхронизации номеров сообщений
		3.0: теперь учитывает максимум mailconfig.fetchlimit
		"""
		if forceReloads:
			loadfrom = 1
			self.msglist = []									# номера сообщений изменились
		else:
			loadfrom = len(self.msglist)+1						# продолжить с места последней загрузки

		# только если загружается вновь поступившая почта
		if loadfrom != 1:
			self.checkSynchError(self.allHdrs())				# возбуждает исключение при рассинхронизации

		# получить все или только новые сообщения
		reply = self.downloadAllHeaders(progress, loadfrom)
		headersList, msgSizes, loadedFull = reply

		for (hdrs, size) in zip(headersList, msgSizes):
			newmsg = MessageInfo(hdrs, size)
			if loadedFull:										# zip может вернуть пустой результат
				newmsg.fulltext = hdrs							# получить полное сообщение, если
			self.msglist.append(newmsg)							# не поддерживается команда ТОР

	def getMessage(self, msgnum):								# получает исходный текст сообщения
		cacheobj = self.msglist[msgnum-1]						# добавляет в кеш, если получено
		if not cacheobj.fulltext:								# безопасно использовать в потоках
			fulltext = self.downloadMessage(msgnum)				# 3.0: более простое кодирование
			cacheobj.fulltext = fulltext
		return cacheobj.fulltext

	def getMessages(self, msgnums, progress=None):
		"""
		получает полный текст нескольких сообщений, может
		вызываться в потоках выполнения;
		2.1: выполняет быструю проверку синхронизации номеров сообщений;
		нельзя получить сообщения здесь, если не было загружено обновление;
		"""
		self.checkSynchError(self.allHdrs())					# возбуждает исключение при рассинхронизации
		nummsgs = len(msgnums)									# добавляет сообщения в кеш
		for (ix, msgnum) in enumerate(msgnums):					# некоторые возможно уже в кеше
			if progress: progress(ix+1, nummsgs)				# подключение только при необходимости
			self.getMessage(msgnum)								# но может выполнять подключение более одного раза

	def getSize(self, msgnum):									# инкапсулирует структуру кеша
		return self.msglist[msgnum-1].fullsize					# уже изменялось однажды!

	def isLoaded(self, msgnum):
		return self.msglist[msgnum-1].fulltext

	def allHdrs(self):
		return [msg.hdrtext for msg in self.msglist]

	def deleteMessages(self, msgnums, progress=None):
		"""
		если удаление всех номеров сообщений возможно, изымает удаленные
		элементы из кеша, но не перезагружает ни список заголовков,
		ни текст уже просмотренных сообщений: список в кеше будет отражать
		изменение номеров сообщений на сервере; если удаление завершилось
		неудачей по каким-либо причинам, вызывающая программа должна
		принудительно перезагрузить все заголовки, расположенные выше,
		потому что номера некоторых сообщений на сервере могут измениться
		непредсказуемым образом;
		2.1: теперь проверяет синхронизацию номеров сообщений, если команда
		ТОР поддерживается сервером; может вызываться в потоках выполнения
		"""
		try:
			self.deleteMessagesSafely(msgnums, self.allHdrs(), progress)
		except mailtools.TopNotSupported:
			mailtools.MailFetcher.deleteMessages(self, msgnums, progress)

		# ошибок не обнаружено: обновить список оглавления
		indexed = enumerate(self.msglist)
		self.msglist = [msg for (ix, msg) in indexed if ix+1 not in msgnums]

class GuiMessageCache(MessageCache):
	"""
	вызовы графического интерфейса добавляются здесь, благодаря чему
	кеш можно использовать в приложениях без графического интерфейса
	"""

	def setPopPassword(self, appname):
		"""
		получает пароль с помощью графического интерфейса, вызывается
		в главном потоке; принудительно вызывается из графического
		интерфейса, чтобы избежать вызова из дочерних потоков выполнения
		"""
		if not self.popPassword:
			prompt = 'Password for %s on %s?' % (self.popUser, self.popServer)
			self.popPassword = askPasswordWindow(appname, prompt)

	def askPopPassword(self):
		"""
		но здесь не использует графический интерфейс: я вызываю его
		из потоков!; попытка вывести диалог в дочернем потоке выполнения
		подвесит графический интерфейс; может вызываться суперклассом
		MailFetcher, но только если пароль остается пустой строкой
		из-за закрытия окна диалога
		"""
		return self.popPassword