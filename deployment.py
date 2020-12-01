#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# Разворачивание пакета
"""
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
"""

import os, sys

print()
cwd = os.getcwd()
version = 'Python' + str(sys.version_info.major) + str(sys.version_info.minor)

syspath = ''
for system in sys.path:
	if system.endswith(version):
		syspath = system + '\lib\site-packages'

filepath = 'pymailgui.pth'
try:
	fp = open(os.path.normpath(os.path.join(syspath, filepath)), 'w')
	fp.write(cwd)
except:
	print(f'Нет доступа к {cwd}. Добавьте файл с путем к рабочей папке вручную')
finally:
	fp.close()

paths = []
with open('SharedNames.py', encoding='utf8') as sn:
	for line in sn:
		if line.startswith('from'):
			paths.append(line[:line.find('#')].strip()[4:])#.split(' import '))

# paths = list(map(str.strip, paths))
paths = {line.split(' import ')[1].strip(): line.split(' import ')[0].strip() for line in paths if line.lstrip().startswith('Tom')}
print(paths)

for path in paths.values():
	inner_paths = path.split('.')
	# print(inner_paths)
	for i in range(1, len(inner_paths)+1):
		folder = os.path.join(cwd, *inner_paths[:i])
		if not os.path.exists(folder):
			os.mkdir(folder)
		# print(folder)
# print(sys.builtin_module_names)

for filename, path in paths.items():
	filepath = os.path.join(cwd, *path.split('.'), filename + '.py')
	currentfile = os.path.join(cwd, filename + '.py')
	if os.path.exists(currentfile):
		os.replace(currentfile, filepath)
		print(filepath)
	else:
		os.replace(currentfile[:-3], filepath[:-3])

startdir = (os.path.join(cwd, 'Tom2\ch14'))
os.mkdir(startdir)

for filename in os.listdir():
	# print(filename)
	if filename == 'guimaker.py' or filename == 'py.ico':
		os.replace(filename, os.path.join(cwd+'\Tom1\ch10', os.path.basename(filename)))
	if filename.endswith('.html') or (filename.endswith('.py') and filename != os.path.basename(__file__)):
		os.replace(filename, os.path.join(startdir, os.path.basename(filename)))
		print(filename)

os.chdir(startdir)
os.system('py setup_config.py')

input ('Please press <Enter>')
