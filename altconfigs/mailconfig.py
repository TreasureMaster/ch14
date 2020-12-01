#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# altconfigs: настройка нескольких учетных записей.
# Пример 14.14 (Лутц Т2 стр.445)
"""
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
"""

above = open('../mailconfgi.py').read()					# скопировать версию из каталога выше
open('mailconfig_book.py', 'w').write(above)			# используется для учетной записи 'book' и как основа для других
acct = input('Account name?')							# book, rmi, train
exec('from mailconfig_%s import *' % acct)				# . первый элемент в sys.path