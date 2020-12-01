#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 14. Почтовый клиент PyMailGUI.
# Реализация PyMailGUI.
# PyMailGUIHelp: текст справки и ее отображение.
# Пример 14.11 (Лутц Т2 стр.441)
"""
##########################################################################
Строка с текстом справки для PyMailGUI и функция отображения справки
в формате HTML;

Предистория: первоначально справка отображалась в окне информационного
диалога, который был узким местом для Linux; позднее стал использоваться
текстовый компонент с прокруткой и кнопки; теперь реализована возможность
отображения справки в формате HTML в веб-браузере;

2.1/3E: строка с текстом справки помещена в отдельный модуль, чтобы
не отвлекать внимание от выполняемого программного кода. В данном случае
этот текст помещается в простое окно с прокруткой; в будущем можно было бы
использовать файл HTML и открывать его в веб-браузере (с помощью модуля
webbrowser или выполняя команду "browser help.html" или "start help.html"
с применением функции os.system);

3.0/4E: теперь также имеется возможность выводить справочный текст
в веб-браузер, в формате HTML, с оформлением списков, ссылок на разделы
и с разделителями; представление справочного текста в формате HTML,
который приводится в виде простой строки ниже и отображается в веб-браузере,
вы найдете в файле PyMailGuiHelp.html, входящем в состав пакета с примерами;
в настоящее время поддерживаются обе версии, текстовая и HTML: измените
параметры в mailconfig.py, чтобы выбрать наиболее предпочтительную для вас;
##########################################################################
"""


# новая справка в формате HTML для 3.0/4E
helpfile = 'PyMailGuiHelp.html'						# смотрите пакет с примерами к книге

def showHtmlHelp(helpfile=helpfile):
	"""
	3.0: открывает HTML-версию справки в локальном веб-браузере с помощью
	модуля webbrowser; этот модуль доступен для импорта, но html-файл может
	оказаться за пределами текущего рабочего каталога
	"""
	import os, webbrowser
	mydir = os.path.dirname(__file__)				# каталог из имени файла этого модуля
	mydir = os.path.abspath(mydir)					# получить абсолютный путь: мог быть .., или иным
	webbrowser.open_new('file://' + os.path.join(mydir, helpfile))


##########################################################################
# строка с текстовой версией справки: за создание графического интерфейса
# отвечает клиент
##########################################################################

helptext = """PyMailGUI, version 3.0
May, 2010 (2.1 January, 2006)
Programming Python, 4th Edition
Mark Lutz, for O'Reilly Media, Inc.

PyMailGUI - это многооконный интерфейс для работы с электронной почтой
в автономном режиме и с подключением к Интернету. Основной интерфейс
этой программы состоит из одного окна со списком писем на почтовом
сервере и нуля или более окон со списками содержимого файлов, куда ранее
сохранялась почта, а также множества окон составления новых сообщений
или просмотра содержимого писем, выбранных в окне со списком.
При запуске первым открывается окно с главным (на сервере) списком
сообщений, но соединение с сервером не устанавливается, пока явно
не будет запущена операция загрузки или отправки сообщения.
Все окна PyMailGUI могут изменяться в размерах, что особенно удобно
для окон со списками, так как это дает возможность отобразить
дополнительные колонки.

Примечание: чтобы использовать PyMailGUI для чтения и отправки вашей
собственной почты, необходимо изменить имена POP и SMTP серверов и параметры
учетной записи в файле mailconfig.py, находящемся в каталоге с исходными
текстами программы PyMailGUI. Подробности смотрите в разделе 11.

Содержание:
0)  РАСШИРЕНИЯ В ЭТОЙ ВЕРСИИ
1)  ОПЕРАЦИИ, ДОСТУПНЫЕ В ОКНЕ СО СПИСКОМ
2)  ОПЕРАЦИИ, ДОСТУПНЫЕ В ОКНЕ ПРОСМОТРА
3)  РАБОТА В АВТОНОМНОМ РЕЖИМЕ
4)  ПРОСМОТР ТЕКСТА И ВЛОЖЕНИЙ
5)  ОТПРАВКА ТЕКСТА И ВЛОЖЕНИЙ
6)  ОДНОВРЕМЕННОЕ ВЫПОЛНЕНИЕ НЕСКОЛЬКИХ ОПЕРАЦИЙ С СЕРВЕРОМ
7)  УДАЛЕНИЕ ПОЧТЫ
8)  СИНХРОНИЗАЦИЯ НОМЕРОВ ВХОДЯЩИХ СООБЩЕНИЙ
9)  ЗАГРУЗКА ПОЧТЫ
10) ПОДДЕРЖКА ЮНИКОДА И ИНТЕРНАЦИОНАЛИЗАЦИИ
11) МОДУЛЬ mailconfig С НАСТРОЙКАМИ
12) ЗАВИСИМОСТИ
13) ПРОЧИЕ ПОДСКАЗКИ ("Шпаргалка")



0) VERSION ENHANCEMENTS

The following lists major enhancements in recent version.

Version 3.0 enhancements:
* Updated to run under Python 3.X (2.X no longer supported without changes)
* Platform-neutral grid() for view window headers, not packed column frames
* Toolbar in message list windows is arranged with separators for clarity  
* Unicode (I18N) encoding support for the full text of fetched/saved messages 
* Unicode (I18N) encoding support for text parts of both fetched and sent mails
* Unicode (I18N) encoding support for message headers in both fetced and sent mails
* Help is now available as both text in a GUI window, and HTML in a browser
* For large inboxes, a new mailconfig setting can limit server headers fetched
* For large inboxes, GUI updates queue speed increased by a factor of 10
* HTML mails now try to extract plain text as an alternative to web browser display
* A Message fetch in progress now disables attempts to fetch the same message
* Multiple recipients separated by "," (not ";"), doesn't clash with email names 
* Replies copy all original recipients initially, by default per mailconfig 


Version 2.1 enhancements:
* View windows now have quick-access buttons for attachments/parts.
* Inbox out-of-synch errors detected on deletes, and index and mail loads.
* Save-file loads and deletes threaded, to avoid pauses for large files.

Version 2.0 enhancements:
* MIME multipart mails with attachments may be both viewed and composed.
* Mail transfers are no longer blocking, and may overlap in time.
* Mail may be saved and processed offline from a local file.
* Message parts may now be opened automatically within the GUI.
* Multiple messages may be selected for processing in list windows.
* Initial downloads fetch mail headers only; full mails are fetched on request.
* View window headers and list window columns are configurable.
* Deletions are performed immediately, not delayed until program exit.
* Most server transfers report their progress in the GUI.
* Long lines are intelligently wrapped in viewed and quoted text.
* Fonts and colors in list and view windows may be configured by the user.
* Authenticating SMTP mail-send servers that require login are supported.
* Sent messages are saved in a local file, which may be opened in the GUI.
* View windows intelligently pick a main text part to be displayed.
* Already fetched mail headers and full mails are cached for speed.
* Date strings and addresses in composed mails are formatted properly.



1) LIST WINDOW ACTIONS

Click list window buttons to process email:

- Load:\t fetch all (or new) mail headers from POP server inbox
- Open:\t load emails from an offline save file into new list window
- Write:\t compose a new email message, send by SMTP
-
- View:\t display selected emails nicely formatted
- Reply:\t compose replies to selected emails, send by SMTP
- Fwd:\t compose forwards of selected emails, send by SMTP
- Save:\t write all selected emails to a chosen save file
- Delete:\t delete selected emails from server or save file
- 
- Quit:\t exit program (server list), close window (file list)

Double-click on an email in a list window's listbox to view the mail's raw text,
including any mail headers not shown by the View button.  List windows opened
for mail save files support all of the above except Load.  After the initial
Load, Load only fetches newly arrived message headers.  To forceably reload all
mails from the server, restart PyMailGUI.  There is reload button, because full
reloads are only required on rare deletion and inbox synchronization errors
(described ahead), and reloads are initiated automatically in these cases.

Click on emails in the main window's listbox to select them.  Click the "All"
checkbox to select all or no emails at once.  More than one email may be
selected at the same time: View, Delete, Reply, Fwd, and Save buttons are
applied to all currently selected emails, in both server and save-file list
windows.  Use Ctrl+click to select multiple mails, Shift+click to select all
from prior selecion, or click+move to drag the selection out.

In 2.1, most of the actions in the server List window automatically run a
quick-check to detect inbox out-of-synch errors with the server.  If a synch
error pop up appears, a full index reload will be automatically run; there
is no need to stop and restart PyMailGUI (see ahead in this help).



2) VIEW WINDOW ACTIONS

Action buttons in message view windows (View):

- Cancel:\t closes the message view window
- Parts:\t lists all message parts, including attachments
- Split:\t extracts, saves, and possibly opens message parts

Actions in message compose windows (Write, Reply, Fwd):

- Cancel:\t closes the message window, discarding its content
- Parts:\t lists files already attached to mail being edited
- Attach:\t adds a file as an attachment to a mail being edited
- Send:\t sends the message to all its recipients

Parts and Split buttons appear in all View windows; for simple messages, the
sole part is the message body.  Message reply, forward, and delete requests are
made in the list windows, not message view windows.  Deletions do not erase
open view windows.

New in 2.1: View windows also have up to a fixed maximum number of quick
access buttons for attached message parts.  They are alternatives to Split.
After the maximum number, a '...' button is added, which simply runs Split.
The maximum number of part buttons to display per view window can be set in
the mailconfig.py user settings module (described ahead).



3) OFFLINE PROCESSING

To process email offline: Load from the server, Save to a local file, and
later select Open to open a save file's list window in either the server List
window or another save file's List window.  Open creates a new List window for
the file, or raises its window if the file is already open.

A save file's list window allows all main window actions listed above, except
for Load.  For example, saved messages can be viewed, deleted, replied to, or
forwarded, from the file's list window.  Operations are mapped to the local
mail save file, instead of the server's inbox.  Saved messages may also be
saved: to move mails from one save file to another, Save and then Delete from
the source file's window.

You do not need to connect to a server to process save files offline: click
the Open button in the main list window.  In a save-file list window, a Quit
erases that window only; a Delete removes the message from the local save file,
not from a server. Save-file list windows are automatically updated when new
mails are saved to the corresponding file anywhere in the GUI.  The sent-mail
file may also be opened and processed as a normal save-mail file, with Open.

Note that Save buttons in list windows save the full message text (including 
its headers, and a message separator).  To save just the main text part of a 
message being viewed or composed, either use the Save button in the text editor
component at the bottom of a view or edit window, or select the "Split" action
button of view windows.  Saves in the text editor component can be useful to 
save a draft of the mail being composed to a temporary file; it can later be 
pasted into a compose window if needed. To save attachments, see the next 
section.

New in 2.1: local save-file Open and Delete requests are threaded to avoid
blocking the GUI during loads and deletes of large files.  Because of this, a
loaded file's index may not appear in its List window immediately.  Similarly,
when new mails are saved or messages are sent, there may be a delay before
the corresponding local file's List window is updated, if it is currently open.

As a status indication, the window's title changes to "Loading..." on loads
and "Deleting..." during deletes, and is reset to the file's name after the thread
exits (the server window uses pop ups for status indication, because the delay
is longer, and there is progress to display).  Eventually, either the index will
appear and its window raised, or an error message will pop up.  Save-file loads
and deletes are not allowed to overlap with each other for a given file, but
may overlap with server transfers and operations on other open files.

Note: save-file Save operations are still not threaded, and may pause the GUI
momentarily when saving very many large mails.  This is normaly not noticeable,
because unlike Open and Delete, saves simply append to the save-file, and do
not reload its content.  To avoid pauses completely, though, don't save very
many large mails in a single operation.

Also note: the current implementation loads the entire save-mail file into
memory when opened.  Because of this, save-mail files are limited in size,
depending upon your computer.  To avoid consuming too much memory, you
should try to keep your save files relatively small (at the least, smaller
than your computer's available memory).  As a rule of thumb, organize your
saved mails by categories into many small files, instead of a few large files.



4) VIEWING TEXT AND ATTACHMENTS

PyMailGUI's view windows use a text-oriented display.  When a mail is viewed,
its main text is displayed in the View window.  This text is taken from the
entire body of a simple message, or the first text part of a multipart MIME
message.  To extract the main message text, PyMailGUI looks for plain text,
then HTML, and then text of any other kind.  If no such text content is found,
nothing is displayed in the view window, but parts may be opened manually with
the "Split" button (and quick-access part buttons in 2.1, described below).

If the body of a simple message is HTML type, or a HTML part is used as the
main message text, a web browser is popped up as an alternative display for
the main message text, if verified by the user (the mailconfig module can be
used to bypass the verification; see ahead).  This is equivalent to opening
the HTML part with the "Split" button, but is initiated automatically for the
main message text's HTML.  If a simple message is something other than text
or HTML, its content must be openened manually with Split.

When viewing mails, messages with multipart attachments are prefixed with
a "*" in list windows.  "Parts" and "Split" buttons appear in all View windows.
Message parts are defined as follows:

- For simple messages, the message body is considered to be the sole
  part of the message.

- For multipart messages, the message parts list includes the main
  message text, as well as all attachments.

In both cases, message parts may be saved and opened with the "Split" button.
For simple messages, the message body may be saved with Split, as well as the
Save button in the view window's text editor.  To process multipart messages:

- Use "Parts" to display the names of all message parts, including any
  attachments, in a pop-up dialog.

- Use "Split" to view message parts: all mail parts are first saved to a
  selected directory, and any well-known and generally safe part files are
  opened automatically, but only if verified by the user.

- See also the note below about 2.1 quick access buttons, for an alternative
  to the Parts/Split interface on View windows.

For "Split", select a local directory to save parts to.  After the save, text
parts open in the TextEditor GUI, HTML and multimedia types open in a web
browser, and common Windows document types (e.g., .doc and .xls files) open via
the Windows registry entry for the filename extension.  For safety, unknown
types and executable program parts are never run automatically; even Python
programs are displayed as source text only (save the code to run manually).

Web browsers on some platforms may open multimedia types (image, audio, video)
in specific content handler programs (e.g., MediaPlayer, image viewers).  No
other types of attachments are ever opened, and attachments are never opened
without user verification (or mailconfig.py authorization in 2.1, described
below).  Browse the parts save directory to open other parts manually.

To avoid scrolling for very long lines (sometimes sent by HTML-based mailers),
the main text part of a message is automatically wrapped for easy viewing.
Long lines are split up at the first delimiter found before a fixed column,
when viewed, replied, or forwarded.  The wrapping column may be configured or
disabled in the mailconfig module (see ahead).  Text lines are never
automatically wrapped when sent; users or recipients should manage line length
in composed mails.

New in 2.1: View windows also have up to a fixed maximum number of quick-access
buttons for attached message parts.  They are alternatives to Split: selecting
an attachment's button automatically extracts, saves, and opens that single
attachment directly, without Split directory and pop-up dialogs (a temporary
directory is used).  The maximum number of part buttons to display per view
window can be set in the mailconfig.py user settings module (described ahead).
For mails with more than the maximum number of attachments, a '...' button is
added which simply runs Split to save and open any additional attachments.

Also in 2.1, two settings in the mailconfig.py module (see section 10) can be
used to control how PyMailGUI opens parts in the GUI:

- okayToOpenParts: controls whether part opens are allowed at all
- verifyPartOpens: controls whether to ask before each part is opened.

Both are used for View window Split actions and part quick-access buttons.  If
okayToOpenParts is False, quick-access part buttons will not appear in the GUI,
and Split saves parts in a directory but does not open them.  verifyPartOpens
is used by both Split and quick-access part buttons: if False, part buttons
open parts immediately, and Split opens all known-type parts automatically
after they are saved (unknown types and executables are never opened).

An additional setting in this module, verifyHTMLTextOpen, controls verification
of opening a web browser on a HTML main text part of a message; if False, the
web browser is opened without prompts.  This is a separate setting from
verifyPartOpens, because this is more automatic than part opens, and some
HTML main text parts may have dubious content (e.g., images, ads).



5) SENDING TEXT AND ATTACHMENTS

To compose an email, use the composition view window to enter its headers, 
add and edit its main message text, and add any attachments.  Message text
is edited in the PyEdit component at the bottom of the window; use its Save 
button to save a draft of your mail's text to a temporary file if desired, 
from which it may be copied and pasted later (see "Offline Processing" for 
more on saves).

When composing new mails, the view window's "Attach" button adds selected files
as attachments, to be sent with the email's main text when the View window's
"Send" is clicked.  Attachment files may be of any type; they are selected in
a pop-up dialog, but are not loaded until Send.  The view window's "Parts"
button displays attachments already added.

The main text of the message (in the view window editor) is sent as a simple
message if there are no attachments, or as the first part of a multipart MIME
message if there are.  In both cases, the main message text is always sent as
plain text.  HTML files may be attached to the message, but there is no support
for text-or-HTML multipart alternative format for the main text, nor for
sending the main text as HTML only.  Not all clients can handle HTML, and
PyMailGUI's text-based view windows have no HTML editing tools.

Multipart nesting is never applied: composed mails are always either a simple
body, or a linear list of parts containing the main message text and attachment
files.

For mail replies and forwards, headers are given intial values, the main
message text (described in the prior section) is wrapped and quoted with '>'
prefixes, and any attachments in the original message are stripped.  Only
new attachments added are sent with the message.

To send to multiple addresses, separate each recipient's address in To, Cc,
and Bcc fields with commas.  For instance:

    PP4E@learning-python.com, "Smith, Bob" <bob@bob.com>, john@nasa.gov

Note that commas can appear both as address separators as well as embedded
in address name components.  Because these are fully parsed when split, it's
okay to use commas in both contexts in recipient lists.  For replies, this 
is handled automatically: the To field is prefilled with From sender in 
the original message, and the Cc field is prefilled with all unique original
mail recipient addresses less the new sender.  Cc and Bcc headers fields are 
ignored if they contain just the initial "?" when sent.

All addresses listed in To, Cc,and Bcc headers are sent the composed mail
message.  To and CC headers are sent in the message itself, but the Bcc
header is not: its content is used only to name recipients, not to generate
a mail header line (that's the main point of a blind copy).  Technically,
Bcc is used for the mail envelope, but not the message text.  The Bcc line
is not enabled by default, but can be enabled in the mailconfig module; as
a convenience, it is prefilled to the sender's addrress, since this is a
common use case (simply delete this text to Bcc to others).  Duplicate email
addresses are removed from the recipients list before mail is sent.  Windows
users: Ctrl-C and Ctrl-V work to copy and paste text in header entry fields.

Successfully sent messages are saved in a local file whose name you list in the
mailconfig.py module.  Sent mails are saved if the variable "sentmailfile" is
set to a valid filename; set to an empty string to disable saves.  This file
may be opened using the Open button of the GUI's list windows, and its content
may be viewed, processed, deleted, saved, and so on within the GUI, just like a
manually saved mail file.  Also like manually saved mail files, the sent-file
list window is automatically updated whenever a new message is sent, if it is
open (there is no need to close and reopen to see new sends).  If this file
grows too large to open, you can delete its content with Delete, after possibly
saving sent mails you wish to keep to another file with Save.

Note that some ISPs may require that you be connected to their systems in order
to use their SMTP servers (sending through your dial-up ISP's server while
connected to a broadband provider may not work--try the SMTP server at your
broadband provider instead), and some SMTP servers may require authentication
(set the "smtpuser" variable in the mailconfig.py module to force authentication
logins on sends).  See also the Python library module smptd for SMTP server
tools; in principle, you could run your own SMTP server locally on 'localhost'.



6) MAIL TRANSFER OVERLAP

PyMailGUI runs mail server transfers (loads, sends, and deletes) in threads, to
avoid blocking the GUI.  Transfers never block the GUI's windows, and windows
do not generally block other windows.  Users can view, create, and process mails
while server transfers are in progress.  The transfers run in the background,
while the GUI remains active.

PyMailGUI also allows mail transfer threads to overlap in time.  In particular,
new emails may be written and sent while a load or send is in progress, and mail
loads may overlap with sends and other mail loads already in progress.  For
example, while waiting for a download of mail headers or a large message, you
can open a new Write window, compose a message, and send it; the send will
overlap with the load currently in progress.  You may also load another mail,
while the load of a large mail is in progress.

While mail transfers are in progress, pop-up windows display their current
progress as a message counter.  When sending a message, the original edit
View window is popped back up automatically on Send failures, to save or retry.
Because delete operations may change POP message numbers on the server, this
operation disables other deletions and loads while in progress.

Offline mail save-file loads and deletes are also threaded: these threads may
overlap in time with server transfers, and with operations on other open save
files.  Saves are disabled if the source or target file is busy with a load
or save operation.  Quit is never allowed while any thread is busy.

Version 3.0 update: if a message's fetch is in progress, it prevents any new
fetch requests that it is a part of, until its fetch completes.  This avoids 
fetching the same message twice, in parallel (a safe, but pointless action).
Other fetches can process in parallel freely if disjoint. 



7) MAIL DELETION

Mail is not removed from POP servers on Load requests, but only on explicit
"Delete" button deletion requests, if verified by the user.  Delete requests
are run immediately, upon user verification.

To delete your mail from a server and process offline: in the server list
window select the All checkbutton, Save to a local file, and then Delete to
delete all mails from the server; use Open to open the save file later to view
and process saved mail.

When deleting from the server window, the mail list (and any already viewed
message text) is not reloaded from server, if the delete was successful.  If
the delete fails, all email must be reloaded, because some POP message numbers
may have changed; the reload occurs automatically.  Delete in a file list
window deletes from the loal file only.

As of version 2.1, PyMailGUI automatically matches messages selected for
deletion with their headers on the mail server, to ensure that the correct
mail is deleted.  If the mail index is out of synch with the server, mails
that do not match the server are not deleted, since their POP message numbers
are no longer accurate.  In this event, an error is displayed, and a full reload
of the mail index list is automatically performed; you do not need to stop and
restart PyMailGUI to reload the index list.  This can slow deletions (it adds
roughly one second per deleted mail on the test machine used), but prevents
the wrong mail from being deleted.  See the POP message number synchronization
errors description in the next section.



8) INBOX MESSAGE NUMBER SYNCHRONIZATION

PyMailGUI does header matching in order to ensure that deletions only delete
the correct messages, and periodically detect synchronization errors with the
server.  If a synchronization error message appears, the operation is cancelled,
and a full index reload from the server is automatically performed.  You need
not stop and restart PyMailGUI and reload the index, but must reattempt the
operation after the reload.

The POP email protocol assigns emails a relative message number, reflecting
their position in your inbox.  In the server List window, PyMailGUI loads its
mail index list on demand from the server, and assumes it reflects the content
of your inbox from that point on.  A message's position in the index list is
used as its POP relative message number for later loads and deletes.

This normally works well, since newly arrived emails are added to the end
of the inbox.  However, the message numbers of the index list can become out
of synch with the server in two ways:

A) Because delete operations change POP relative message numbers in the inbox,
deleting messages in another email client (even another PyMailGUI instance)
while the PyMailGUI server list window is open can invalidate PyMailGUI's
message index numbers.  In this case, the index list window may be arbitrarily
out of synch with the inbox on the server.

B) It is also possible that your ISP may automatically delete emails from
your inbox at any time, making PyMailGUI's email list out of synch with message
numbers on the mail server.  For example, some ISPs may automatically move an
email from the inbox to the undeliverable box, in response to a fetch failure.
If this happens, PyMailGUI's message numbers will be off by one, according to
the server's inbox.

To accommodate such cases, PyMailGUI 2.1 always matches messages to be deleted
against the server's inbox, by comparing already fetched headers text with the
headers text returned for the same message number; the delete only occurs if
the two match.  In addition, PyMailGUI runs a quick check for out-of-synch
errors by comparing headers for just the last message in the index, whenever
the index list is updated, and whenever full messages are fetched.

This header matching adds a slight overhead to deletes, index loads, and mail
fetches, but guarantees that deletes will not remove the wrong message, and
ensures that the message you receive corresponds to the item selected in the
server index List window.  The synch test overhead is one second or less on
test machines used - it requires 1 POP server connect and an inbox size and
(possibly) header text fetch.

In general, you still shouldn't delete messages in PyMailGUI while running a
different email client, or that client's message numbers may become confused
unless it has simlar synchronization tests.  If you receive a synch error
pop up on deletes or loads, PyMailGUI automatically begins a full reload of
the mail index list displayed in the server List window.



9) LOADING EMAIL

To save time, Load requests only fetch mail headers, not entire messages.
View operations fetch the entire message, unless it has been previously viewed
(already loaded messages are cached).  Multiple message downloads may overlap
in time, and may overlap with message editing and sends.

In addition, after the initial load, new Load requests only fetch headers of
newly arrived messages.  All headers must be refetched after a delete failure,
however, due to possibly changed POP message numbers.

PyMailGUI only is connected to a mail server while a load, send, or delete
operation is in progress.  It does not connect at all unless one of these
operations is attempted, and disconnects as soon as the operation finishes.
You do not need any Internet connectivity to run PyMailGUI unless you attempt
one of these operations.  In addition, you may disconnect from the Internet
when they are not in progress, without having to stop the GUI--the program
will reconnect on the next transfer operation.

Note: if your POP mail server does support the TOP command for fetching mail
headers (most do), see variable "srvrHasTop" in the mailtools.py module to
force full message downloads.

Also note that, although PyMailGUI only fetches message headers initially if
your email server supports TOP (and has a faster GUI actions queue in 3.0),
this initial fetch can still take some time for very large inboxes; as a rule
of thumb, use save-mail files and deletions to keep your inbox small.

3.0 Update: to address the prior paragraph's issue, see the new "fetchlimit"
setting in the mailconfig module section ahead; this allows you to limit how 
many headers PyMailGUI will attempt to fetch, making it practical to use for
large inboxes and slow Internet access or mail servers.



10) UNICODE AND INTERNATIONALIZATION SUPPORT

In Version 3.0, there is now support for Unicode (Internationalization) 
encodings for fetched, saved, and sent mails, as allowed by the Python 3.1 
email package. A user-configurable setting in the mailconfig module is used
on a session-wide basis to decode full message bytes into Unicode strings 
when fetched, and to encode and decode mail messages stored in text-mode 
save files.

More visibly, when composing, the main text and attached text parts of 
composed mails may be given explicit Unicode encodings in mailconfig or 
via user input; when viewing, message header information of parsed emails 
is used to determine the Unicode types of both the main mail text as well 
as text parts opened on demand. In addition, Internationalized mail headers
(e.g., "Subject", "From:") are decoded per email, MIME, and Unicode standards
when displayed, per their own content, and are automatically encoded if
non-ASCII when sent. 

Here is how all these policies play out in terms of user interfaces:

* Fetched emails: 
  When fetching mails, a session-wide user setting is used to decode full message
  bytes to Unicode strings, as required by Python's current email parser; if this
  fails, a handful of guesses are applied. Most mail text will likely be 7 or 8 
  bit in nature, since ASCII is the original standard.

* Composed text parts: 
  When sending new mails, user settings are used to determine Unicode type for 
  the main text part, and any text attachment parts. If these are not set in 
  mailconfig, the user will instead be asked for encoding names in the GUI for
  each text part. These are ultimately used to add character set headers, and 
  to invoke MIME encoding. In all cases, the program falls back on UTF-8 if the
  user's encoding setting or input does not work for the text being sent; for
  instance, if the user has chosen ASCII for the main text of a reply or forward 
  to a non-ASCII message, or for non-ASCII attachments.

* Composed headers: 
  When sending new mails, if header lines or the name component of an email address
  in address-related lines does not encode properly as ASCII text, we first encode 
  the header per email Internationalization standard. This is done per UTF-8 by 
  default, but a mailconfig setting can request a different encoding.  In email 
  address pairs, names which cannot be encoded are dropped, and only the email 
  address is used. It is assumed that servers will respect the encoded names in 
  email addresses.

* Displayed text parts: 
  When vieweing fetched mail, Unicode encodings names in message headers are 
  used to decode the main text part into str Unicode text prior to inserting it
  into a PyEdit component. The content of all other text parts, as well as all
  binary parts, is saved in bytes form in binary-mode files, from where they may 
  be opened later in the GUI on demand. When such text parts are opened, they are
  displayed in PyEdit pop-up windows by passing to PyEdit the name of the part's
  binary-mode file, as well as the part's encoding name obtained from part message
  headers. If this encoding name is absent or fails to decode, PyEdit's separate 
  Unicode policies are applied (see Chapter 11). HTML text parts are saved in 
  binary mode and opened in a web browser, relying on the browser's own character
  set support.

* Displayed headers:
  When viewing email, message headers are automatically decoded per email standards.
  This includes both full headers such as Subject, as well as the name components 
  of all email address fields in address-related headers such as From, To, and Cc. 

The user setting of the mailconfig module that applies to the last of these
points is used across an entire PyMailGUI session to decode message bytes 
to text prior to parsing, and to save and load full message text to save 
files.  Users may set this to a Unicode encoding name string which works for
their mails' encodings; 'latin1', 'utf8', and 'ascii' are reasonable guesses
for most emails. If this encoding fails, other common encodings are tried,
and as a last resort the message is still displayed if its headers can be 
decoded, but its body is changed to an error message; to view such mails, 
try running PyMailGUI again with a different encoding. 

There is currently no special support for Unicode encodings of the full 
text of sent mails in general, apart from that inherited from Python's 
libraries. 



11) THE mailconfig CONFIGURATION MODULE

Change the mailconfig.py module file in PyMailGUI's home directory on your
own machine to reflect your email server names, username, email address, and
optional mail signature line added to all composed mails.

Most settings in this module are optional, or have reasonable preset defaults.
However, you must minimally set this module's "smtpservername" variable to send
mail, and its "popservername" and "popusername" to load mail from a server.
These are simple Python variables assigned to strings in this file.  See the
module file and its embedded comments for details.

The mailconfig module's "listheaders" attribute can also be set to a tuple of
string header field name, to customize the set of headers displayed in list
windows; mail size is always displayed last.  Similarly mailconfig's
"viewheaders" attribute can extend the set of headers shown in a View window
(though From, To, Cc, and Subject fields are always shown).  List windows
display message headers in fixed-width columns.

Variables in the mailconfig module also can be used to tailor the font used in
list windows ("fontsz"), the column at which viewed and quoted text is
automatically wrapped ("wrapsz"), colors and fonts in various windows, the
local file where sent messages are saved, the opening of mail parts, and more;
see the file's source code for more details.

New in version 3.0: the "fetchEncoding" setting in this file is used across
an entire PyMailGUI session to decode message bytes to text prior to parsing, 
and to save and load full message text to save files. Set this to a Unicode
encoding name which works for your mails ('latin1', 'utf8', and 'ascii' are 
reasonable guesses for most emails). If this encoding along with a few guesses
fails, the message will still appear if its headers can be decoded, but its 
body is changed to an error message; try running again with a different encoding
name to view.

New in version 3.0: for sending new mails, "mainTextEncoding" and 
"attachmentTextEncoding" are used to specify Unicode encodings for main mail
text, plus all text attachments.  Set these to None to be prompted for encodings
on mail sends, otherwise the assignments to these names are used across the 
entire session (if you "Cancel" when asked, they both default to 'latin-1').
Set these to sys.getdefaultencoding() result to apply the platform default.
The system falls back on UTF-8 if your selections do not match text to be sent.

New in version 3.0: "headersEncodeTo" is used to encode non-ASCII headers (and
email address names in headers) if it is not None; if None, UTF-8 is the default.

New in version 3.0: PyMailGUI loads only mail headers initially, and only 
newly-arrived headers thereafter. Depending on your Internet and server speeds,
though, this may still be impractical for very large inboxes. To support such 
cases, a new mailconfig setting, "fetchlimit," can be used to limit the number 
of headers (or full mails if TOP is unsupported) fetched on loads: given this
setting N, PyMailGUI fetches at most N of the most recently arrived mails. 
Older mails outside this set are not fetched from the server, but are displayed
as empty/dummy emails which are mostly inpoperative (though they may be fetchable)

New in version 3.0: If "repliesCopyToAll" is True, the Reply operation prefills
the reply's Cc line with all original mail recipients, after removing duplicates 
and the new sender.  If it is False, ot CC prefill occurs, and the reply is
configured to reply to the original sender only.  The Cc line may always be edited
later, in either case.
 
Note: use caution when changing this file, as PyMailGUI may not run at all if
some of its variables are missing.  You may wish to make a backup copy before
editing it in case you need to restore its defaults.  A future version of this
system may have a configuration dialog which generates this module's code.

See also: textConfig.py here, for configuring the appearance of pop-up PyEdit
windows created by PyMailGUI for test parts, raw mail, and source code (the
mailconfig module configures the main text PyEdit component only).



12) DEPENDENCIES

This client-side program currently requires Python and tkinter.  It uses Python
threads, if installed, to avoid blocking the GUI.  Sending and loading email
from a server requires an Internet connection.  Requires Python 3.0 or later,
and uses the Python Python 3.1 version of the "email" standard library module
to parse and compose mail text.  Reuses a number of modules located in the 
PP4E examples tree.



13) ПРОЧИЕ ПОДСКАЗКИ ("Шпаргалка")

- Используйте ',' для разделения адресов в заголовках To, Cc и Bcc.
- Адреса могут указываться в полной форме '"name" <addr>'.
- Содержимое и заголовки декодируются при получении и кодируются при отправке.
- Сообщения в формате HTML отображаются как простой текст, плюс как HTML в веб-браузере.
- Заголовки To, Cc и Bcc получают значения, укзанные при составлении письма,
  но заголовок Bcc не отправляется.
- Если разрешено в mailconfig, заголовок Bcc заполняется адресом отправителя.

- При составлении ответа и при пересылке в письмо автоматически вставляется
  текст оригинального сообщения.
- Если разрешено, при составлении ответа заголовок Сс заполняется адресами
  получателей оригинального письма.
- При отправке письма в него можно добавлять вложения, которые будут
  кодироваться при необходимости.
- Вложения могут открываться в окне просмотра, щелчком на кнопке
  или на кнопках быстрого доступа.
- Двойной щелчок на сообщении в окне со списком открывает окно с исходным
  текстом сообщения.
- Можно выбрать сразу несколько сообщений в списке, чтобы обработать их
  как единое множество: Ctrl|Shift + щелчок, или флажок All.

- Отправляемая почта сохраняется в файле, имя которого указано в mailconfig:
  открыть его для просмотра можно с помощью кнопки Open.
- Операция сохранения открывает диалог выбора файла, куда будет
  сохранено сообщение.
- Операция сохранения никогда не удаляет выбранный файл, а добавляет
  сообщение в конец.
- Операция извлечения вложений (Split) запрашивает каталог сохранения;
  кнопки быстрого доступа сохраняют вложения в каталоге ./TempParts.
- Диалоги открытия и сохранения файла всегда запоминают последний каталог.
- Для сохранения черновика письма во время его составления используйте
  операцию сохранения редактора.

- Пароли запрашиваются программой PyMailGUI по мере необходимости
  и не сохраняются.
- Вы можете сохранить свои пароли в файл и указать его имя в mailconfig.py.
- Чтобы напечатать текст сообщения, сохраните его "Save" в текстовый файл
  и напечатайте с помощью другого инструмента.
- В каталоге altconfigs вы увидите примеры использования нескольких
  учетных записей.

- Письма никогда не удаляются с почтового сервера автоматически.
- При успешном завершении операция удаления не вызывает перезагрузку
  заголовков.
- Операция удаления предварительно проверяет почтовый ящик,
  чтобы гарантировать удаление выбранной почты.
- Операция получения письма определяет изменения в ящике входящей почты
  и может автоматически перезагрузить оглавление.
- Одновременно может выполняться любое количество операций отправки
  и получения неперсекающихся множеств писем.

- Щелкните на кнопке Source в этом окне, чтобы увидеть
  исходные тексты PyMailGUI.
- Смотрите обновления и изменения на сайте http://www.rmi.net/~lutz.
- Эта система распространяется с открытыми исходными текстами: изменяйте
  ее программный код по своему усмотрению.
"""

if __name__ == '__main__':
	print(helptext)							# вывести в stdout, если запущен как сценарий
	input('Press Enter key')				# пауза, если запущен щелчком мыши
