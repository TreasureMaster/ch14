#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# Интерактивная конфигурация соединения
"""
# ---------------------------------------------------------------------------- #
Прототип настроечного файла для изменения настроек конфигурационного файла
PyMailGUI. Выводит и изменяет не все параметры. Можно расширить по своему
усмотрению (цвета, фонт и его размеры и т.п.).
# ---------------------------------------------------------------------------- #
"""

from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator
from Tom1.ch10 import windows

class PyMailConfigWindow(windows.MainWindow):

	appname = 'PyMailGUI 3.0'

	def __init__(self):
		windows.MainWindow.__init__(self, self.appname, 'configuration')
		self.parseConfig()
		self.makeWidgets()

	def makeWidgets(self):
		self.makeGrid()
		Button(text='Save', command=self.onSave).pack(side=LEFT)
		Button(text='Help', command=self.commonHelp).pack(side=RIGHT)
		Button(text='Quit', command=self.quit).pack(side=RIGHT)

	def makeGrid(self):
		configs = Frame(self)
		configs.pack(side=TOP, expand=YES, fill=BOTH)

		self.entFields = []
		for i, (var, name) in enumerate(self.variables().items()):
			# print(i, var)
			if name == 'separator':
				Separator(configs, orient=HORIZONTAL).grid(row=i, sticky=EW, columnspan=2)
			else:
				lab = Label(configs, text=name, justify=LEFT, anchor=W)
				lab.bind('<Button-3>', self.onHelp)
				if var == 'sslServerMode':
					self.sslMode = BooleanVar()
					self.sslMode.set(True if self.config[var] == 'True' else False)
					ent = Checkbutton(configs, text='SSL', anchor=W)
					ent.config(variable=self.sslMode, command=self.sslOn)
				else:
					ent = Entry(configs)
					ent.insert(0, self.config[var])
					self.entFields.append((ent, lab))
				lab.grid(row=i, column=0, sticky=EW)
				ent.grid(row=i, column=1, sticky=EW)
				configs.rowconfigure(i, weight=1)
		configs.columnconfigure(1, weight=1)

	def onHelp(self, event):
		# print(event.widget.cget('text'))
		varname = self.inverse_variables()[event.widget.cget('text')]
		showinfo(self.appname, self.descHelp()[varname])
		# print(varname)

	def commonHelp(self):
		showinfo(self.appname,
			"Код формирования конфигурации запуска PyMailGUI в файле myconfig.py.\n"
			"\n"
			"  1) кнопка Help - это описание;\n"
			"  2) кнопка Quit - выход из программы;\n"
			"  3) кнопка Save - сохранить конфигурацию в файл.\n"
			"\n"
			"Щелчок правой кнопкой мыши на описании атрибута выводит подробную помощь для этого атрибута."
		)

	def sslOn(self):
		pass
		# print(self.sslMode.get())

	def onSave(self):
		fieldvalues = {self.inverse_variables()[entry[1].cget('text')] : entry[0].get() for entry in self.entFields}
		markDesc = False
		with open('baseconfig.py', encoding='utf8') as base, open('myconfig.py', 'w', encoding='utf8') as myfile:
			for line in base:
				line = line.strip()
				if line[:3] == '"""':
					markDesc = False if markDesc else True
					print(line, file=myfile)
					continue
				if markDesc or not line:
					print(line, file=myfile)
					continue
				Var = line.split()[0]
				if Var in fieldvalues:
					value = repr(fieldvalues[Var]) if fieldvalues[Var] != 'None' else None
					print(Var, '=', value, file=myfile)
				elif Var == 'sslServerMode':
					print(Var, '=', self.sslMode.get(), file=myfile)
				else:
					print(line, file=myfile)

	def variables(self):
		return {
			'sslServerMode': 'SSL требуется?',
			'0': 'separator',
			'popservername': 'Сервер POP3',
			'popusername' : 'Пользователь POP3',
			'1': 'separator',
			'smtpservername': 'Сервер SMTP',
			'smtpuser': 'Пользователь SMTP',
			'2': 'separator',
			'myaddress': 'Адрес e-mail',
			'mysignature': 'Подпись в письме',
			'3': 'separator',
			'fetchEncoding': 'Декодирование текста сообщения',
			'mainTextEncoding': 'Кодировка для новых писем',
			'attachmentTextEncoding': 'Кодировка текстовых вложений',
			'headersEncodeTo': 'Кодирование заголовков и адресов',
			'4': 'separator'
		}

	def inverse_variables(self):
		return dict(zip(self.variables().values(), self.variables().keys()))

	def parseConfig(self):
		markDesc = False									# маркировка начала длинного описания в 3 кавычках
		markComment = ['#', '']								# виды комментариев
		self.config = {}
		with open('baseconfig.py', encoding='utf8') as fc:
			for line in fc:
				line = line.lstrip()
				if line[:3] == '"""':
					markDesc = False if markDesc else True
					continue
				if markDesc or not line:
					continue
				if line[0] not in markComment:
					line = line[:line.find('#')].rstrip()
					# print(line)
					if '=' in line:
						name, value = line.split('=', 1)
						self.config[name.strip()] = value.strip('() "\'')

	def descHelp(self):
		return {
			'sslServerMode': 'Настраивает тип соединения - с SSL или без',
			'popservername': 'Название сервера входящей почты POP3',
			'popusername': 'Учетная запись POP3',
			'smtpservername': 'Название сервера исходящей почты SMTP',
			'smtpuser': 'Учетная запись SMTP',
			'myaddress': 'Адрес электронной почты e-mail',
			'mysignature': 'Ваша подпись в письме',
			'fetchEncoding': 'Кодировка, используемая для декодирования текста сообщения, и для кодирования/декодирования при сохранении сообщения в файле.',
			'mainTextEncoding': 'Кодировка, используемая при создании текста новых писем.',
			'attachmentTextEncoding': 'Кодировка, используемая для текстовых вложений письма',
			'headersEncodeTo': 'Кодировка для заголовков писем и имен в адресах электронной почты (для новых писем при отправке).'
		}

if __name__ == '__main__':
	root = PyMailConfigWindow()
	root.mainloop()
