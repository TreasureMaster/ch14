#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# SharedNames: глобальные переменные среды.
# Пример 14.2 (Лутц Т2 стр.385)
"""
# ---------------------------------------------------------------------------- #
объекты, своместно используемые всеми классами окон и главным модулем:
глобальные переменные
# ---------------------------------------------------------------------------- #
"""

# используется во всех окнах, заголовки
appname = 'PyMailGUI 3.0'

# используется операциями сохранения, открытия, удаления из списка;
# а также для файла, куда сохраняются отправленные сообщения
saveMailSeparator = 'PyMailGUI' + ('-'*60) + 'PyMailGUI\n'

# просмтариваемые в настоящее время файлы; а также для файла,
# куда сохраняются отправленные сообщения
openSaveFiles = {}											# 1 окно на файл, {имя: окно}

# источник конфигурационного файла mailconfig.py
from Tom2.ch13.mailtools.mailSender import MailSender
from resolvingConfig import mailconfig

# службы стандартной библиотеки
import sys, os, email.utils, email.message, webbrowser, mimetypes
from tkinter import *
from tkinter.simpledialog import askstring
from tkinter.filedialog import SaveAs, Open, Directory
from tkinter.messagebox import showinfo, showerror, askyesno

# повторно используемые примеры из книги
from Tom1.ch10 import windows								# рамка окна, протокол завершения
from Tom1.ch10 import threadtools							# очередь обработчиков в потоках
# FIXME импортирование mailconfig в mailtools ?
from Tom2.ch13 import mailtools								# утилиты загрузки, отправки, анализа, создания
# FIXME импортирование модулей для TextEditor
from Tom1.ch11.TextEditor import textEditor					# компонент и окно

# print('config path SharedNames:', mailconfig.__file__)

# модули, определяемые здесь
# localuse = False  # выбор использования модуля пользовательских настроек
# mailconfig = __import__('maillocal' if localuse else 'myconfig')		# пользовательские параметры: серверы, шрифты и т.д.
import popuputil														# диалоги вывода справки, информации о ходе выполнения операции
import wraplines														# перенос длинных строк
import messagecache														# запоминает уже загруженную почту
import html2text														# упрощенный механизм преобразования html->text
import PyMailGuiHelp													# документация пользователя

def printStack(exc_info):
	"""
	отладка: выводит информацию об исключениях и трассировку стека в stdout;
	3.0: выводит трассировочную информацию в файл журнала, если вывод
	в sys.stdout терпит неудачу: это происходит при запуске из другой
	программы в Windows; без этого обходного решения PyMailGUI аварийно
	завершает работу, поскольку вызывается из главного потока при появлении
	исключения в дочернем потоке; вероятно ошибка в Python 3.1:
	эта проблема отсутствует в версиях 2.5 и 2.6, и объект с трассировочной
	информацией прекрасно работает, если вывод осуществляется в файл;
	по иронии, простой вызов print() здесь тоже работает (но вывод
	отправляется в никуда) при запуске из другой прграммы;
	"""
	print(exc_info[0])
	print(exc_info[1])
	import traceback

	try:
		traceback.print_tb(exc_info[2], file=sys.stdout)				# ок, если не запущена из другой программы
	except:
		log = open('_pymailerrlog.txt', 'a')							# использовать файл, иначе завершится в 3.х, но не в 2.5/6
		log.write('-'*80)
		traceback.print_tb(exc_info[2], file=log)

# счетчики рабочих потоков выполнения, запущенных этим графическим интерфейсом
# sendingBusy используется всеми программами отправки,
# используется операцией завершения главного окна
loadingHdrsBusy = threadtools.ThreadCounter()							# только 1
deletingBusy = threadtools.ThreadCounter()								# только 1
loadingMsgsBusy = threadtools.ThreadCounter()							# может быть множество
sendingBusy = threadtools.ThreadCounter()								# может быть множество
