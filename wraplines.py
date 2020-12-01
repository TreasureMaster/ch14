#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# wraplines: инструменты разбиения строк.
# Пример 14.7 (Лутц Т2 стр.427)
"""
# ---------------------------------------------------------------------------- #
разбивает строки по фиксированной позиции или по первому разделителю перед
фиксированной позицией; смотрите также: иной, но похожий модуль textwrap
в стандартной библиотеке (2.3+);
4Е предупреждение: предполагается работа со строками str; поддержка строк
типа bytes могла бы помочь избежать некоторых сложностей с декодированием;
# ---------------------------------------------------------------------------- #
"""

defaultsize = 80

def wrapLinesSimple(lineslist, size=defaultsize):
	"""
	разбивает по фиксированной позиции
	"""
	wraplines = []
	for line in lineslist:
		while True:
			wraplines.append(line[:size])					# ОК, если длин строки < size
			line = line[size:]								# разбить без анализа
			if not line: break
	return wraplines

def wrapLinesSmart(lineslist, size=defaultsize, delimiters='.,:\t '):
	"""
	выполняет перенос по первому разделителю левее позиции size
	"""
	wraplines = []
	for line in lineslist:
		while True:
			if len(line) <= size:
				wraplines += [line]
				break
			else:
				for look in range(size-1, size // 2, -1):
					if line[look] in delimiters:
						front, line = line[:look+1], line[look+1:]
						break
				else:
					front, line = line[:size], line[size:]
				wraplines += [front]
	return wraplines

# ---------------------------------------------------------------------------- #
#                  утилиты для типичных случаев использования                  #
# ---------------------------------------------------------------------------- #

def wrapText1(text, size=defaultsize):						# лучше для текста из строк: письмо
															# сохраняет первоначальную структуру строк
	"""
	когда текст читается целиком
	"""
	lines = text.split('\n')								# разбить по \n
	lines = wrapLinesSmart(lines, size)						# перенести по разделителям
	return '\n'.join(lines)									# объединить все вместе

def wrapText2(text, size=defaultsize):						# более равномерное разбиение
															# но теряется первоначальная структура строк
	"""
	то же, но текст - одна строка
	"""
	text = text.replace('\n', ' ')							# отбросить \n, если имеются
	lines = wrapLinesSmart([text], size)					# перенести единую строку по разделителю
	return lines											# объединение выполняет вызывающий

def wrapText3(text, size=defaultsize):
	"""
	то же, но выполняет объединение
	"""
	lines = wrapText2(text, size)							# перенос как одной, длинную строку
	return '\n'.join(lines) + '\n'							# объединить, добавляя \n

def wrapLines1(lines, size=defaultsize):
	"""
	когда символ перевода строки добавляется в конец
	"""
	lines = [line[:-1] for line in lines]					# отбросить '\n' (или .rstrip)
	lines = wrapLinesSmart(lines, size)						# перенести по разделителям
	return [(line + '\n') for line in lines]				# объединить

def wrapLines2(lines, size=defaultsize):					# более равномерное разбиение
															# но теряется первоначальная структура
	"""
	то же, но объединяет в одну строку
	"""
	text = ''.join(lines)									# объединить в 1 строку
	lines = wrapText2(text)									# перенести по разделителям
	return [(line + '\n') for line in lines]				# добавить '\n' в концы строк

# ---------------------------------------------------------------------------- #
#                               самотестирование                               #
# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
	lines = [
		'spam ham ' * 20 + 'spam,ni' * 20,
		'spam ham ' * 20,
		'spam,ni' * 20,
		'spam ham.ni' * 20,
		'',
		'spam' * 80,
		' ',
		'spam ham eggs'
	]
	sep = '-' * 30
	# "Сырой" вывод, без форматирования
	print('all', sep)
	for line in lines: print(repr(line))
	# Просто делит по длина строки по умолчанию - 80
	print('simple', sep)
	for line in wrapLinesSimple(lines): print(repr(line))
	# Делит по длине строки по умолчанию (80), но с учетом символов-разделителей (.,: и т.п.)
	print('smart', sep)
	for line in wrapLinesSmart(lines): print(repr(line))

	# аналогично первым двум, но с длиной строки 60
	print('single1', sep)
	for line in wrapLinesSimple([lines[0]], 60): print(repr(line))
	print('single2', sep)
	for line in wrapLinesSmart([lines[0]], 60): print(repr(line))
	# добавляет к каждой разбитой строке символ \n
	print('combined text', sep)
	for line in wrapLines2(lines): print(repr(line))
	print('combined lines', sep)
	print(wrapText1('\n'.join(lines)))

	assert ''.join(lines) == ''.join(wrapLinesSimple(lines, 60))
	assert ''.join(lines) == ''.join(wrapLinesSmart(lines, 60))
	print(len(''.join(lines)), end=' ')
	print(len(''.join(wrapLinesSimple(lines))), end=' ')
	print(len(''.join(wrapLinesSmart(lines))), end=' ')
	print(len(''.join(wrapLinesSmart(lines, 60))))
	input('Press Enter')										# пауза, если сценарий был запущен щелчком мыши