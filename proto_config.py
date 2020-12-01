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
Rev.1.1: можно выбирать из нескольких конфигурационных файлов; если настройка
отсутствует в файле, то она помечается как пропущенная и отключается возможность
ее редактирования; если редактируемый файл сохоаняется под тем же именем,
то в папку OldConfigs зааписывается его последняя версия;
Rev.1.1: вместо имени файла используется объект PathName из модуля pathname;
TODO можно подключить редактирование пропущенных настроек <setting skipped>;
данные настройки должны включаться в новый файл при включении или удалятся
из него при отключении;
TODO не решена задача с обратными косыми слешами в подписи конфигурации
mysignature; из-за их "умножения" в tkinter их количество увеличивается
от файла к файлу; механизм не ясен, т.к. в подписи может находиться
как управляющий символ, так и экранированная обратная косая черта;
# ---------------------------------------------------------------------------- #
"""
import os
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename, Open, LoadFileDialog
from tkinter.ttk import Separator
from Tom1.ch10 import windows
from Tom2.ch14.pathname import *

# список имен возможных файлов конфигурации
config_filenames = ['mailconfig.py', 'baseconfig.py', 'maillocal.py', 'myconfig.py', 'protoconfig.py']
# имя по умолчанию, куда будет сохраняться конфигурация
save_config = 'mailconfig.py'

class PyMailConfigWindow(windows.MainWindow):

	appname = 'PyMailGUI 3.0'

	def __init__(self, inconfig=config_filenames[0], outconfig=save_config):
		inconfig = askopenfilename(title='Выбрать файл для редактирования', initialdir='.') or inconfig
		self.inconfig = self.setPathname(inconfig)
		outconfig = askopenfilename(title='Выбрать файл для сохранения', initialdir='.') or outconfig
		self.outconfig = self.setPathname(outconfig)
		windows.MainWindow.__init__(self, self.appname, 'configuration')
		self.parseConfig()
		self.makeWidgets()

	def setPathname(self, path):
		if not os.path.exists(path):
			open(path, 'w').close()
		return PathName(path)

	def makeWidgets(self):
		"""
		конвейер создания виджетов, отрисовка их в основном фрейме
		"""
		self.makeFileMenu()
		self.makePathLabel()
		self.makeGrid()
		self.makeBottomMenu()

	def makeFileMenu(self):
		"""
		определяет меню выбора конфигурационного файла
		"""
		# TODO возможно, вместо меню создать кнопку загрузки нужного файла?
		setfile = Frame(self)
		setfile.pack(side=TOP, expand=YES, fill=X)
		self.sourcefile = StringVar(self)
		self.sourcefile.set(self.files()[0])
		filemenu = OptionMenu(setfile, self.sourcefile, *self.files())
		filemenu.config(anchor=W)
		filemenu.pack(side=LEFT, expand=YES, fill=X)
		Button(setfile, text='Set config file', command=self.setNewSourceFile).pack(side=RIGHT)

	def makePathLabel(self):
		"""
		определяет метки описания путей нового и старого конфигурационных файлов
		(черный фон)
		"""
		pathlabel = Frame(self)
		pathlabel.pack(side=TOP, expand=YES, fill=X)
		Label(pathlabel, text='Исходный файл:', fg='light grey', bg='black', anchor=W).pack(fill=X)
		self.inlabelpath = Label(pathlabel, fg='light grey', bg='black', anchor=W)
		self.inlabelpath.pack(fill=X)
		self.inlabelfile = Label(pathlabel, fg='light grey', bg='black', anchor=W)
		self.inlabelfile.pack(fill=X)
		Separator(pathlabel, orient=HORIZONTAL).pack(side=TOP)
		Label(pathlabel, text='Новый файл:', fg='light grey', bg='black', anchor=W).pack(fill=X)
		self.outlabelpath = Label(pathlabel, fg='light grey', bg='black', anchor=W)
		self.outlabelpath.pack(fill=X)
		self.outlabelfile = Label(pathlabel, fg='light grey', bg='black', anchor=W)
		self.outlabelfile.pack(fill=X)
		self.changePathLabelText()

	def changePathLabelText(self):
		"""
		изменения текста меток описания путей конфигурационных файлов
		"""
		self.inlabelpath.config(text='Путь:   ' + self.inconfig.Dirname)
		self.inlabelfile.config(text='Файл:  ' + self.inconfig.Basename)
		self.outlabelpath.config(text='Путь:   ' + self.outconfig.Dirname)
		self.outlabelfile.config(text='Файл:  ' + self.outconfig.Basename)

	def makeGrid(self, redrawGrid=False):
		"""
		создает виджет-таблицу с настройками конфигурационного файла
		"""
		if redrawGrid:
			self.grid.destroy()
		self.grid = Frame(self)
		self.grid.pack(side=TOP, expand=YES, fill=BOTH)

		self.entFields = []
		for i, (var, name) in enumerate(self.variables().items()):
			# print(i, var)
			if name == 'separator':
				Separator(self.grid, orient=HORIZONTAL).grid(row=i, sticky=EW, columnspan=2)
			else:
				isVarSet = var in self.config
				lab = Label(self.grid, text=name, justify=LEFT, anchor=W)
				lab.bind('<Button-3>', self.onHelp)
				if var == 'sslServerMode' and isVarSet:
					self.sslMode = BooleanVar()
					self.sslMode.set(True if self.config[var] == 'True' else False)
					rowframe = Checkbutton(self.grid, text='SSL', anchor=W)
					rowframe.config(variable=self.sslMode, command=self.sslOn)
				else:
					rowframe = Frame(self.grid)
					ent = Entry(rowframe)
					if isVarSet:
						ent.insert(0, self.config[var])
					else:
						# если настройки нет в конфигурационном файле
						ent.insert(0, '<setting skipped>')
						ent.config(state=DISABLED)
						Button(rowframe, text='Enable', command=lambda: 0).pack(side=RIGHT)
					ent.pack(side=LEFT, expand=YES, fill=X)
					self.entFields.append((ent, lab))
				lab.grid(row=i, column=0, sticky=EW)
				rowframe.grid(row=i, column=1, sticky=EW)
				self.grid.rowconfigure(i, weight=1)
		self.grid.columnconfigure(1, weight=1)

	def makeBottomMenu(self):
		bottom = Frame(self)
		bottom.pack(side=BOTTOM, expand=YES, fill=BOTH)

		Button(bottom, text='Save', command=self.onSave).pack(side=LEFT)
		Button(bottom, text='Help', command=self.commonHelp).pack(side=RIGHT)
		Button(bottom, text='Quit', command=self.quit).pack(side=RIGHT)

# ------------------------------ Команды кнопок ------------------------------ #

	def setNewSourceFile(self):
		# print(self.sourcefile.get())
		self.inconfig = self.setPathname(self.sourcefile.get())
		self.changePathLabelText()
		self.parseConfig()
		self.makeGrid(redrawGrid=True)

	def onHelp(self, event):
		# print(event.widget.cget('text'))
		varname = self.inverse_variables()[event.widget.cget('text')]
		showinfo(self.appname, self.descHelp()[varname])
		# print(varname)

	def commonHelp(self):
		"""
		Help - обработчик кнопки, выводит общий help программы
		"""
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
		"""
		Save - обработчик кнопки, сохраняет введенные данные конфигурации
		в конфигурационном файле
		"""
		fieldvalues = {self.inverse_variables()[entry[1].cget('text')] : entry[0].get() for entry in self.entFields}
		markDesc = False
		if self.inconfig == self.outconfig:
			self.inconfig.saveAsOld()
			self.changePathLabelText()
		with open(self.inconfig.Absname, encoding='utf8') as base, open(self.outconfig.Absname, 'w', encoding='utf8') as myfile:
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
					try:
						value = int(value.strip("'"))
					except:
						pass
					print(Var, '=', value, file=myfile)
				elif Var == 'sslServerMode':
					print(Var, '=', self.sslMode.get(), file=myfile)
				else:
					print(line, file=myfile)

# ------------------------------- Конфигурации ------------------------------- #

	def files(self):
		# TODO сканировать текущую директорию на наличие конфигурационных файлов
		return config_filenames

	def variables(self):
		"""
		словарь описаний данных конфигурационного файла
		"""
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
			'4': 'separator',
			'fetchlimit': 'Максимальное число сообщений',
			'5': 'separator'
		}

	def inverse_variables(self):
		"""
		инвертирует словарь описания данных конфигурационного файла,
		заменяя по схеме: ключ:значение -> значение:ключ
		"""
		return dict(zip(self.variables().values(), self.variables().keys()))

	def parseConfig(self):
		"""
		считывает настройки конфигурационного файла и создает список настроек
		типа 'название': 'значение'
		"""
		markDesc = False									# маркировка начала длинного описания в 3 кавычках
		markComment = ['#', '']								# виды комментариев
		self.config = {}
		with open(self.inconfig.getAbsname(), encoding='utf8') as fc:
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
		"""
		словарь значений краткого Help
		используется при щелчке правой кнопки мыши на настройке в таблице
		"""
		return {
			'sslServerMode': 'Настраивает тип соединения - с SSL или без',
			'popservername': 'Название сервера входящей почты POP3',
			'popusername': 'Учетная запись POP3',
			'smtpservername': 'Название сервера исходящей почты SMTP',
			'smtpuser': 'Учетная запись SMTP',
			'myaddress': 'Адрес электронной почты e-mail',
			'mysignature': 'Ваша подпись в письме. Внимание! Не используйте специальные символы с бэкслешем. Редактируйте подпись вручуню, если они необходимы.',
			'fetchEncoding': 'Кодировка, используемая для декодирования текста сообщения, и для кодирования/декодирования при сохранении сообщения в файле.',
			'mainTextEncoding': 'Кодировка, используемая при создании текста новых писем.',
			'attachmentTextEncoding': 'Кодировка, используемая для текстовых вложений письма',
			'headersEncodeTo': 'Кодировка для заголовков писем и имен в адресах электронной почты.',
			'fetchlimit': 'Максимальное число самых "свежих" заголовков/сообщений, загружаемых по запросу.'
		}

if __name__ == '__main__':
	import sys
	infilename = (len(sys.argv) > 1 and sys.argv[1]) or config_filenames[0]
	outfilename = (len(sys.argv) > 2 and sys.argv[2]) or save_config
	root = PyMailConfigWindow(inconfig=infilename, outconfig=outfilename)
	root.mainloop()
