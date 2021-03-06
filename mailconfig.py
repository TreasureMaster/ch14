#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# mailconfig: настройки пользователя.
# Пример 14.9 (Лутц Т2 стр.434)
"""
# ---------------------------------------------------------------------------- #
Пользовательские настройки для PyMailGUI.

Сценарии для работы с электронной почтой получают имена серверов и другие
параметры из этого модуля: измените модуль так, чтобы он отражал имена ваших
серверов, вашу подпись и предпочтения. Этот модуль также определяет
некоторые параметры внешнего вида виджетов в графическом интерфейсе,
политику выбора кодировок Юникода и многие другие особенности версии 3.0.
Смотрите также: локальный файл textConfig.py, где хранятся настройки
редактора PyEdit, используемого программой PyMailGUI.

Внимание: программа PyMailGUI не работает без большинства переменных в этом
модуле: создайте резервную копию! Предупреждение: с некоторого момента
в этом файле непоследовательно используется смешивание регистров символов
в именах переменных...; Что сделать: некоторые настройки можно было бы
получать из командной строки и неплохо было бы реализовать возможность
настройки параметров в виде диалогов графического интерфейса, но и этот
общий модуль тоже неплохо справляется с задачей.
# ---------------------------------------------------------------------------- #
"""

# ---------------------------------------------------------------------------- #
# (обязательные параметры для соединения с сервером) - тип соединения SSL
# ---------------------------------------------------------------------------- #

sslServerMode = False

# ---------------------------------------------------------------------------- #
# (обязательные параметры для загрузки, удаления) сервер POP3, пользователь;
# ---------------------------------------------------------------------------- #

# popservername = '?Please set your mailconfig.py attributes?'

popservername = 'pop3.xplore.loc'
popusername = 'test@test.loc'

# ---------------------------------------------------------------------------- #
# (обязательные параметры отправки) имя сервера SMTP;
# смотрите модуль Python smtpd, где имеется класс сервера SMTP,
# выполняющийся локально ('localhost');
# примечание: провайдер Интернета может требовать, чтобы вы напрямую
# подключались к его системе: у меня был случай, когда я мог отправлять
# почту через Earthlink, используя коммутируемое подключение,
# но не мог по кабельному соединению Comcast;
# ---------------------------------------------------------------------------- #

smtpservername = 'smtp.xplore.loc'

# ---------------------------------------------------------------------------- #
# (необязательные параметры) личная информация, используемая PyMailGUI
# для заполнения полей в формах редактирования;
# если не установлено, не будет вставлять начальные значения;
# mysignature - может быть блоком текста в тройных кавычках,
# пустая строка игнорируется;
# myaddress - используется как начальное значение поля 'From',
# если не пустое, больше не пытается определить значение From для ответов -
# с переменным успехом;
# Внимание! Невозможно использовать управляющие символы строки в программе
# с графическим интерфейсом. Мы не можем предположить, что находиться в строке -
# управляющий символ или экранированный бэкслеш. Теоретически можно сделать
# парсинг подписи, однако проще редактировать подпись вручную.
# ---------------------------------------------------------------------------- #

myaddress = 'test@test.loc'
mysignature = 'Thanks, --IZRUSKA--'

# ---------------------------------------------------------------------------- #
# (может потребоваться при отправке) пользователь/пароль SMTP,
# если необходима аутентификация;
# если аутентификация не требуется, установите переменную smtpuser
# в значение None или '' и присвойте переменной smtppasswdfile имя файла
# с паролем SMTP, или пустую строку, если желательно заставить программу
# запрашивать пароль (в консоли или в графическом интерфейсе)
# ---------------------------------------------------------------------------- #

# smtpuser = None													# зависит от провайдера
smtpuser = 'test@test.loc'
smtppasswdfile = ''												# присвойте '', чтобы заставить запрашивать пароль

# smtpuser = popusername

# ---------------------------------------------------------------------------- #
# (необязательные параметры) PyMailGUI: имя локального однострочного
# текстового файла с паролем к РОР-серверу; если пустая строка
# или файл не может быть прочитан, пароль будет запрашиваться
# при первой попытке подключения;
# пароль не шифруется: оставьте эту переменную пустой при работе
# на общем компьютере; PyMailCGI всегда запрашивает пароль
# (выполняется, возможно, на удаленном сервере);
# ---------------------------------------------------------------------------- #

# poppasswdfile = r'.\passwd\pymailgui.txt'							# присвойте '', чтобы запрашивать пароль
poppasswdfile = ''

# ---------------------------------------------------------------------------- #
# (обязательные параметры) локальный файл для сохранения
# отправленных сообщений; этот файл можно открыть и просмотреть,
# щелкнув на кнопке 'Open' в PyMailGUI; не используйте форму '.',
# если программа может запускаться из другого каталога: например, pp4e demos
# ---------------------------------------------------------------------------- #

# sentmailfile = r'.\mails\sentmail.txt'								# . означает текущий рабочий каталог

# sourcedir = r'c:\...\PP4E\Inernet\Email\PyMailGUI'
# sentmailfile = sourcedir + 'sentmail.txt'

# определить автоматически по одному из файлов с исходными текстами
import wraplines, os
mysourcedir = os.path.dirname(os.path.abspath(wraplines.__file__))
sentmailfile = os.path.join(mysourcedir, 'sentmail.txt')

# ---------------------------------------------------------------------------- #
# (более не используется) локальный файл, куда pymail сохраняет принятую
# почту (полный текст); PyMailGUI запрашивает имя файла с помощью диалога
# в графическом интерфейсе; кроме того, операция Split запрашивает каталог,
# а кнопки быстрого доступа к частям сохраняют их в ./TempParts;
# ---------------------------------------------------------------------------- #

# savemailfile = r'c:\mails\savemail.txt'								# не используется в PyMailGUI: диалог

# ---------------------------------------------------------------------------- #
# (необязательные параметры) списки заголовков, отображаемых в окнах
# со списками и в окнах просмотра в PyMailGUI; listheaders замещает список
# по умолчанию, viewheaders расширяет его; оба должны быть кортежами строк
# или None, чтобы использовать значение по умолчанию;
# ---------------------------------------------------------------------------- #

listheaders = ('Subject', 'From', 'Date', 'To', 'X-Mailer')
viewheaders = ('Bcc',)

# ---------------------------------------------------------------------------- #
# (необязательные параметры) шрифты и цвета для текста в окнах со списками,
# содержимого в окнах просмотра и кнопок быстрого доступа к вложениям;
# шрифты определяются кортежами ('семейство', размер, 'стиль'); цвет (фона
# и переднего плана) определяется строкой 'имя_цвета' или шестнадцатиричным
# значением '#RRGGBB'; None означает значение по умолчанию; шрифты и цвета
# окон просмотра могут также устанавливаться интерактивно, с помощью
# меню Tools текстового редактора; смотрите также пример setcolor.py
# в части книги, посвященной графическим интерфейсам (глава 8);
# ---------------------------------------------------------------------------- #

listbg = 'indianred'										# None, 'white', '#RRGGBB'
listfg = 'black'
listfont = ('courier', 10, 'bold')
viewheight = 18												# максимальное число строк при открытии (20)

partfg = None
partbg = None

# смотрите имена цветоа в Тк: aquamarine paleturquoise powderblue
# goldenrod burgundy ....
# listbg = listfg = listfont = None
viewbg = viewfg = viewfont = viewheight = None			# использовать по умолчанию
# partbg = partfg = None

# ---------------------------------------------------------------------------- #
# (необязательные параметры) позиция переноса строк оригинального текста
# письма при просмотре, создании ответа и пересылке; перенос выполняется
# по первому разделителю левее данной позиции;
# при редактировании не выполняется автоматический перенос строк: перенос
# должен выполняться самим пользователем или инструментами электронной
# почты получателя; чтобы запретить перенос строк, установите в этом
# параметре большое значение (1024?);
# ---------------------------------------------------------------------------- #

wrapsz = 90

# ---------------------------------------------------------------------------- #
# (необязательные параметры) управляют порядком открытия вложений
# в графическом интерфейсе PyMailGUI; используются при выполнении
# операции Split в окнах просмотра и при нажатии кнопок быстрого доступа
# к вложениям; если параметр okayToOpenParts имеет значение False, кнопки
# быстрого доступа не будут отображаться в графическом интерфейсе,
# а операция Split будет сохранять вложения в каталоге, но не будет
# открывать их; параметр verifyPartOpens используется кнопкoй Split
# и кнопками быстрого доступа: если этот параметр имеет значение False, все
# вложения с известными типами автоматически будут открываться кнопкой Split;
# параметр verifyHTMLTextOpen определяет, следует ли использовать
# веб-браузер для открытия основной текстовой части в формате HTML;
# ---------------------------------------------------------------------------- #

okayToOpenParts = True										# открывать ли части/вложения вообще?
verifyPartOpens = False										# спрашивать ли разрешение перед открытием каждой части?
verifyHTMLTextOpen = False									# спрашивать ли разрешение перед открытием основной
# текстовой части, если она в формате HTML?

# ---------------------------------------------------------------------------- #
# (необязательные параметры) максимальное число кнопок быстрого доступа
# к частям сообщения, отображаемых в середине окон просмотра;
# если количество частей окажется больше этого числа, после кнопки
# с порядковым номером, соответствующим ему, будет отображаться
# кнопка "...", нажатие на которую будет запускать операцию "Split"
# для извлечения дополнительных частей;
# ---------------------------------------------------------------------------- #

maxPartButtons = 8											# количество кнопок в окнах просмотра

# *** дополнительные параметры для версии 3.0 ***

# ---------------------------------------------------------------------------- #
# (обязательные параметры, для получения сообщений) кодировка Юникода,
# используемая для декодирования полного текста сообщения и для кодирования
# и декодирования текста сообщения при сохранении в текстовых файлах;
# подробности смотрите в главе 13: это ограниченное и временное решение
# пока в пакете email не будет реализован новый механизм анализа сообщений,
# способный работать со строками bytes, способный более точно обрабатывать
# кодировки на уровне отдельных сообщений;
# обратите внимание: для декодирования сообщений в некоторых старых файлах
# я был вынужден использовать не utf-8, а 'latin1' (8-битовую кодировку,
# которая является надмножеством 7-битовой кодировки ascii);
# ---------------------------------------------------------------------------- #

fetchEncoding = 'latin-1'

# ---------------------------------------------------------------------------- #
# (необязательные параметры, для отправки) кодировки для текста новых писем
# плюс всех текстовых вложений; установите эти параметры равными None, чтобы
# программа запрашивала кодировки при отправке письма, в противном случае
# эти значения будут действовать на протяжении всего сеанса;
# по умолчанию = 'latin-1', если в диалоге запроса кодировки щелкнуть
# на кнопке Cancel; в любом случае, если кодировки, указанные здесь
# или введенные в диалоге, окажутся непримениыми, будет использоваться
# кодировка UTF-8 (например, при выборе ascii для отправки письма с текстом
# или вложением, содержащим символы вне диапазона ascii); пакет email более
# првередлив к именам кодировок, чем сам язык Python: ему известна
# кодировка latin-1 (будет использовать формат MIME quoted-printable), но
# кодировка latin1 ему не известна (будет использовать формат MIME base64);
# чтобы задействовать кодировку по умолчанию для текущей платформы,
# присвойте этим параметрам значение, возвращаемое функцией
# sys.getdefaultencoding(); кодировки текстовых частей полученных
# сообщений определяются автоматически из заголовков;
# ---------------------------------------------------------------------------- #

mainTextEncoding = 'ascii'
attachmentTextEncoding = 'ascii'

# ---------------------------------------------------------------------------- #
# (необязательные параметры, для отправки) определите в этом параметре имя
# кодировки, которая будет применяться к заголовкам и к именам в адресах,
# содержашим символы вне диапазона ASCII, при отправке новых писем;
# None означает использование кодировки UTF-8 по умолчанию, которая подходит
# в большинстве случаев; имена в адресах электронной почты, которые
# не удастся декодировать, будут отбрасываться (будут использоваться только
# сами адреса); обратите внимание, что декодирование заголовков выполняется
# автоматически перед отображением note, в соответствии с их содержимым,
# без учета пользовательских настроек;
# ---------------------------------------------------------------------------- #

headersEncodeTo = None

# ---------------------------------------------------------------------------- #
# (необязательные параметры) выбирают текстовую, HTML или обе версии справки;
# всегда отображается та или иная версия: если оба параметра отключены,
# отображается версия HTML
# ---------------------------------------------------------------------------- #

showHelpAsText = True										# прокручиваемый текст, с кнопками открытия файлов
# с исходным программынм кодом
showHelpAsHTML = True										# HTML в веб-браузере, без ссылок на файлы с исходным
# программным кодом

# ---------------------------------------------------------------------------- #
# (необязательный параметр) если имеет значение True, выбранная текстовая
# часть сообщения в формате HTML не будет отображаться в окне PyEdit;
# если она отображается в веб-браузере; если имеет значение False, будут
# отображаться обе версии и будет выполнено определение кодировки
# для передачи текстовому виджету (которая может быть неизвестна браузеру);
# ---------------------------------------------------------------------------- #

skipTextOnHtmlPart = False									# не показывать текст из разметки html в PyEdit

# ---------------------------------------------------------------------------- #
# (необязательный параметр) максимальное количество заголовков или сообщений,
# которые будут загружаться по каждому запросу; если установить в этом
# параметре значение N, PyMailGUI будет загружать не более N самых свежих
# почтовых сообщений; более старые сообщения, не вошедшие в это число,
# не будут загружаться с сервера, но будут отображатсья как пустые/фиктивные
# сообщения; если этот параметр будет иметь значение None (или 0)?
# загрузка никак не будет ограничиваться; используйте этот параметр,
# если у вас слишком много сообщений в пoчтовом ящике и скорость подключения
# к Интернету или почтового сервера делает процедуру загрузки всех писем
# слишком длительной; кроме того, PyMailGUI загружает заголовки только самых
# новых сообщений, но данный параметр никак не зависит от этой особенности;
# ---------------------------------------------------------------------------- #


fetchlimit = 50

# ---------------------------------------------------------------------------- #
# (необязательные параметры) начальные ширина и высота списка с оглавлением
# (символы х строки); исключительно для удобства, поскoльку окно легко может
# растягиваться после открытия;
# ---------------------------------------------------------------------------- #

listWidth = None											# None = используется значение по умолчанию 74
listHeight = None											# None = используется значение по умолчанию 15

# ---------------------------------------------------------------------------- #
# (необязательный параметр, для ответов) если имеет значение True,
# операция Reply будет заполнять заголовок Сс ответа адресами всех
# получателей оригинального сообщения, после удаления повторяющихся адресов,
# и адресом нового отправителя; если имеет значение False, заголовок Сс
# заполняться не будет и ответ будет настроен на отправку только отправителю
# оригинального сообщения; в любом случае, заголoвок Сс всегда можно
# отредактировать позднее.
# ---------------------------------------------------------------------------- #

repliesCopyToAll = True										# True = ответить отправителю + всем получателям,
# иначе - только отпарвителю

# end
