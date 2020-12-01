#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# html2text: извлечение текста из разметки HTML (прототип, предварительное знакомство).
# Пример 14.8 (Лутц Т2 стр.431)
"""
# ---------------------------------------------------------------------------- #
*ОЧЕНЬ* простой механизм преобразования html-в-текст для получения
цитируемого текста в операциях создания ответа и пересылки и отображения
при просмотре основного содержимого письма. Используется, только когда
основная текстовая часть представлена разметкой HTML (то есть отсутствует
альтернативная или другие текстовые части для отображения). Нам также
необходимо знать, является текст разметкой HTML или нет, однако уже
findMainText возвращает тип содержимого для основной текстовой части.

Данная реализация является лишь прототипом, который поможет вам создать
более законченное решение. Она не подвергалась сколько-нибудь существенной
доводке, но любой результат лучше, чем отображение исходного кода разметки
HTML, и гораздо более удачной выглядит идея перехода к использованию виджета
просмотра/редактирования HTML в будущем. Однако на данный момент PyMailGUI
все еще ориентирована на работу с простым текстом.

Если (в действительности - когда) этот механизм не сможет воспроизвести
простой текст, пользователи смогут просмотреть и скопировать текст в окне
веб-браузера, запускаемого для просмотра HTML. Подробнее об анализе HTML
рассказывается в главе 19.
# ---------------------------------------------------------------------------- #
"""

from html.parser import HTMLParser							# стандартный парсер (SAX-подобная модель)

class Parser(HTMLParser):									# наследует стандартный парсер, определяет обработчики
	def __init__(self):										# текст - строка str, может быть в любой кодировке
		HTMLParser.__init__(self)
		self.text = '[Extracted HTML text]'
		self.save = 0
		self.last = ''

	def addtext(self, new):
		if self.save > 0:
			self.text += new
			self.last = new

	def addeoln(self, force=False):
		if force or self.last != '\n':
			self.addtext('\n')

	def handle_starttag(self, tag, attrs):					# + другие, с которых может начинаться содержимое?
		if tag in ('p', 'div', 'table', 'h1', 'h2', 'li'):
			self.save += 1
			self.addeoln()
		elif tag == 'td':
			self.addeoln()
		elif tag == 'style':
			self.save -= 1
		elif tag == 'br':
			self.addeoln(True)
		elif tag == 'a':
			alts = [pair for pair in attrs if pair[0] == 'alt']
			if alts:
				name, value = alts[0]
				self.addtext('[' + value.replace('\n', '') + ']')

	def handle_endtag(self, tag):
		if tag in ('p', 'div', 'table', 'h1', 'h2', 'li'):
			self.save -= 1
			self.addeoln()
		elif tag == 'style':
			self.save += 1

	def handle_data(self, data):
		data = data.replace('\n', '')						# а как быть с тегом <PRE>?
		data = data.replace('\t', ' ')
		if data != ' ' * len(data):
			self.addtext(data)

	def handle_entityref(self, name):
		xlate = dict(lt='<', gt='>', amp='&', nbsp='').get(name, '?')
		if xlate:
			self.addtext(xlate)								# плюс множество других: показать ? как есть

def html2text(text):
	try:
		hp = Parser()
		hp.feed(text)
		return (hp.text)
	except:
		return text


if __name__ == "__main__":
	# для тестирования: html2text.py media\html2text-test\htmlmail1.html
	# получает имя файла из командной строки, отображает результат в Text
	# файл должен содержать текст в кодировке по умолчанию для данной
	# платформы, но это требование не применяется к аргументу text
	
	import sys, tkinter
	text = open(sys.argv[1], 'r').read()
	text = html2text(text)
	t = tkinter.Text()
	t.insert('1.0', text)
	t.pack()
	t.mainloop()