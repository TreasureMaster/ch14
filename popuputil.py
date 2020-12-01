#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# popuputil: диалоги общего назначения.
# Пример 14.6 (Лутц Т2 стр.425)
"""
# ---------------------------------------------------------------------------- #
вспомогательные окна - могут пригодиться в других программах
# ---------------------------------------------------------------------------- #
"""

from tkinter import *
from Tom1.ch10.windows	import PopupWindow

class HelpPopup(PopupWindow):
	"""
	специализированная версия Toplevel, отображающая
	справочный текст в области с прокруткой
	кнопка Source вызывает указанный обработчик обратного вызова
	альтернатива в версии 3.0: использовать файл HTML и модуль webbrowser
	"""
	myfont = 'system'										# настраивается
	mywidth = 78											# 3.0: начальная ширина

	def __init__(self, appname, helptext, iconfile=None, showsource=lambda:0):
		PopupWindow.__init__(self, appname, 'Help', iconfile)
		from tkinter.scrolledtext import ScrolledText		# немодальный диалог
		bar = Frame(self)									# присоединяется первым - усекается последним
		bar.pack(side=BOTTOM, fill=X)
		code = Button(bar, bg='beige', text='Source', command=showsource)
		quit = Button(bar, bg='beige', text='Cancel', command=self.destroy)
		code.pack(pady=1, side=LEFT)
		quit.pack(pady=1, side=LEFT)
		text = ScrolledText(self)							# добавить Text + полосы прокрутки
		text.config(font=self.myfont)
		text.config(width=self.mywidth)						# слишком большоя для showinfo
		text.config(bg='steelblue', fg='white')				# закрыть при нажатии на кнопку
		text.insert('0.0', helptext)						# или на клавишу Return
		text.pack(expand=YES, fill=BOTH)
		self.bind('<Return>', (lambda event: self.destroy()))

def askPasswordWindow(appname, prompt):
	"""
	модальный диалог для ввода строк пароля
	функция getpass.getpass использует stdin, а не графический интерфейс
	tkSimpleDialog.askstring() выводит ввод эхом
	"""
	win = PopupWindow(appname, 'Prompt')				# настроенный экземпляр Toplevel
	Label(win, text=prompt).pack(side=LEFT)
	entvar = StringVar(win)
	ent = Entry(win, textvariable=entvar, show='*')		# показывать *
	ent.pack(side=RIGHT, expand=YES, fill=X)
	ent.bind('<Return>', lambda event: win.destroy())
	ent.focus_set()
	win.grab_set()
	win.wait_window()
	win.update()										# update() вызывает принудительную перерисовку
	return entvar.get()									# виджет get() к этому моменту уже уничтожен

class BusyBoxWait(PopupWindow):
	"""
	блокирующее окно с сообщением: выполнение потока приостанавливается
	цикл обработки событий главного потока графического интерфейса
	продолжает выполняться, но сам графический интерфейс не действует,
	пока открыто это окно; используется переопределенная версия метода
	quit, потому что в дереве наследования он находится ниже, а не левее;
	"""
	def __init__(self, appname, message):
		PopupWindow.__init__(self, appname, 'Busy')
		self.protocol('WM_DELETE_WINDOW', lambda:0)			# игнорировать попытку закрыть
		label = Label(self, text=message + '...')			# win.quit(), чтобы закрыть окно
		label.config(height=10, width=40, cursor='watch')	# курсор занятости
		label.pack()
		self.makeModal()
		self.message, self.label = message, label

	def makeModal(self):
		self.focus_set()									# захватить фокус ввода
		self.grab_set()										# ждать вызова threadexit

	def changeText(self, newtext):
		self.label.config(text=self.message + ': ' + newtext)

	def quit(self):
		self.destroy()										# не запрашивать подтверждение

class BusyBoxNowait(BusyBoxWait):
	"""
	неблокирующее окно
	вызывайте changeText, чтобы отобразить ход выполнения операции,
	quit - чтобы закрыть окно
	"""
	def makeModal(self):
		pass


if __name__ == "__main__":
	HelpPopup('spam', 'See figure 1...\n')
	print(askPasswordWindow('spam', 'enter password'))
	input('Enter to exit')									# пауза, если сценарий запущен щелчком мыши