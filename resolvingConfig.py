#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Сценарий выбора конфигурационного файла.
"""
# ---------------------------------------------------------------------------- #
программа используется только для выбора загрузки конфигурационного файла;
True - выполняется загрузка конфигурации для сервера локальной сети,
False - выполняется загрузка конфигурации для внешнего сервера
# ---------------------------------------------------------------------------- #
"""

import sys, os
# '..' - для сценария самотестирования mailtools
sys.path.insert(0, os.path.abspath('..'))
# '.' - для директории запуска файла
sys.path.insert(0, os.path.abspath('.'))

# print(sys.path)

localserver = True
mailconfig = __import__('maillocal') if localserver else __import__('mailconfig')
print('config path:', mailconfig.__file__)

# print('fetchlimit' in mailconfig.__dict__)