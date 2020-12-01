#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# Инкапсуляция работы с именем файла
"""
# ---------------------------------------------------------------------------- #
Инкапсулирует работу с путем и именем файла.
Просто используются свои собственные названия для методов модуля os.path;
# ---------------------------------------------------------------------------- #
"""
import os
import re

class SymbolPathNameError(Exception): pass

# задает паттерн пдля префикса или суффикса файла
affix_pattern = re.compile(r'^[\w-]*$')

class PathName:
	
	def __init__(self, pathname):
		self.pathname = os.path.normpath(os.path.abspath(pathname))

	# оформление как свойства
	@property
	def Absname(self):
		return self.getAbsname()

	@property
	def Basename(self):
		return self.getBasename()

	@property
	def Dirname(self):
		return self.getDirname()

	def getAbsname(self):
		return self.pathname

	def getBasename(self):
		return os.path.basename(self.pathname)

	# def getCleanname(self):
	# 	return os.path.splitext(self.getBasename())[0]

	def getDirname(self):
		return os.path.dirname(self.pathname)

	def getExtension(self):
		return os.path.splitext(self.pathname)[1]

	def getWithoutExtension(self):
		return os.path.splitext(self.pathname)[0]

	def isExists(self):
		return os.path.exists(self.pathname)

	def isCorrectCharacters(self, chars):
		return bool(affix_pattern.match(chars))

	def addPrefix(self, prefix):
		# TODO можно регулировать длину префикса и суффикса
		if self.isCorrectCharacters(prefix):
			self.pathname = os.path.normpath(os.path.join(self.getDirname(), prefix + '_' + self.getBasename()))
		else:
			raise SymbolPathNameError('invalid character in prefix')

	def addSuffix(self, suffix):
		if self.isCorrectCharacters(suffix):
			self.pathname = os.path.normpath(self.getWithoutExtension() + '_' + suffix + self.getExtension())
		else:
			raise SymbolPathNameError('invalid character in suffix')

	def __eq__(self, other):
		if self.getBasename() == other.getBasename():
			return True
		return False

	def saveAsOld(self):
		"""
		создает папку OldConfigs, если она не существует,
		переименовывает сам себя, добавляя суффикс 'old',
		и перемещает себя в созданную папку, сохраняя
		ссылку на самого себя в новой папке
		"""
		oldconfig = os.path.normpath(os.path.join(os.getcwd(), 'OldConfigs'))
		if not os.path.exists(oldconfig):
			os.mkdir(oldconfig)
		oldpath = self.pathname
		self.addSuffix('old')
		self.pathname = os.path.normpath(os.path.join(oldconfig, self.getBasename()))
		if os.path.exists(self.pathname): os.remove(self.pathname)
		os.rename(oldpath, self.pathname)


if __name__ == "__main__":
	path = PathName('pathname.py')
	print()
	print(path.getAbsname())
	print('property:', path.Absname)
	print(path.getDirname())
	print(path.getBasename())
	print('property:', path.Basename)
	print(path.isExists())
	print(path.getExtension())
	# print(path.getCleanname())
	print(path.getWithoutExtension())
	print('-'*40)
	print(path.isCorrectCharacters('adsadGKJHK'))
	print(path.isCorrectCharacters('asdaGG32'))
	print(path.isCorrectCharacters('asdaGG32-423khk'))
	print(path.isCorrectCharacters('asdaGG32_423khk'))
	print(path.isCorrectCharacters('asdaGG32_423khk-!*?'))
	print('-'*40)
	path.addPrefix('new')
	print(path.getAbsname())
	path.addSuffix('old')
	print(path.getAbsname())
	try: path.addPrefix('973fu*&^%*')
	except Exception as msg: print(msg)
	print('-'*40)
	path = PathName('pathname.py')
	path1 = PathName('pathname.py')
	print(path == path1)
	path2 = PathName('myconfig.py')
	print(path == path2)
	# path.addOldConfigSubdir()
	print('-'*40)
	if not os.path.exists('testrename.txt'):
		open('testrename.txt', 'w').close()
	path3 = PathName('testrename.txt')
	print(path3.getAbsname())
	path3.saveAsOld()
	print(path3.getAbsname())
