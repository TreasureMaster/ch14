# Описание этапов работы тестирования программы PyMailGUI

# ------------------------------- Главное окно ------------------------------- #

# [x] Запуск программы
# [x] Первая загрузка почты работает (кнопка Load)
# [x] Повторное нажатие Load ничего не скачивает, если не было новых писем
# [х] Повторное нажатие Load после удаления сообщения выводит ошибку синхронизации и перезагружает письма с сервера
# [х] Повторное нажатие Load при добавлении новых сообщений скачивает только новые письма
# [x] Выводит ошибку при неправильно введенном пароле или логине

# [x] Выбор одного сообщения и просмотр его (кнопка View)
# [x] Выбор нескольких сообщений с помощью CTRL или SHIFT и просмотр их (кнопка View)
# [x] Выбор всех сообщений с помощью чекбокса All и просмотр их (кнопка View)
# [x] Загружает сообщения с сервера, если они еще не были загружены в этом сеансе (одно или несколько)
# [x] Двойной щелчок мыши на сообщении выводит его в необработанном виде (вместе с всеми заголовками)

# [x] Справка по PyMailGUI (текст и браузер) (верхняя синяя кнопка help)
# Внутри окна справки:
# [x] Закрывает окно help (кнопка Cancel)
# [x] Показывает исходные тексты программ из окна help (кнопка Source)

# [x] Удаление писем
# [x] Удаляет одно или более выбранных писем с сервера (кнопка Delete)
# [x] Проверяет синхронизацию писем при удалении

# [x] Сохранение писем
# [x] Сохраняет одно или несколько выбранных писем в файле (кнопка Save)

# [x] Выход из программы (кнопка Quit)

# ------------------------- Окно просмотра сообщения ------------------------- #

# [x] Выводит список присоединенных к сообщению файлов (кнопк Parts)
# [x] Сохраняет части сообщения в указанный каталог и открывает их все (кнопка Split)
# [x] Закрывает окно просмотра сообщения (кнопка Cancel)
# [x] Открывает выбранный присоединенный файл (соответствующая кнопка с названием файла, кнопка быстрого доступа)
# [x] Если присоединенных файлов слишком много, то добавляется кнопка ... (аналог кнопки Split)
# [x] Если письмо содержит HTML, то отображается простой текст и есть возможность открыть HTML в браузере
# TODO Не декодирует русское название почты вида (имя <e-mail>) при получении почты
# [x] Декодирует русское название почты вида (имя <e-mail>) при отправке почты

# --------------------------- Многопоточная модель --------------------------- #

# 1) В процессе загрузки с сервера:
# 	[х] можно изменять графический интерфейс
# 	[х] можно составлять другие письма
# 	[х] можно отправлять другое письмо
# 	[х] можно отправлять несколько других писем
# 	[ ] нельзя инициировать другие операции с сервером (отправка, загрузка писем) во время удаления писем (слишком быстро, не могу протестировать)
# 	[x] нельзя повторно начать загружать письма уже во время их загрузки

# ------------------- Обработка без подключения к интернету ------------------ #

# [x] Сохраняет (в новый файл или добавляет в старый) выбранное количество сообщений в файл (кнопка Save)
# [x] Открывает файл с сообщениями для просмотра (кнопка Open)
# [x] Может быть открыто любое количество окон с сообщениями из файлов (и одно с сервера)
# [x] Просмотр сообщения (письма) из файла (кнопка View)
# [x] Удаляет сообщения (письма) из файла (кнопка Delete)

# -------------------------- Окно отправки сообщения ------------------------- #

# [x] Открывает диалог отправки нового сообщения (кнопка Write)
# [x] Закрывает окно после запроса подтверждения (кнопка Cancel)
# [x] Отправляет письмо на сервер (кнопка Send)
# [x] Можно использовать полную форму адреса (имя + <адрес>)
# FIXME Выдает ошибку при использовании полной формы адреса без скобок (имя + адрес), но отправляет письмо
# NOTE добавил свое исправление в mailtools.mailParser.splitAddresses
# FIXME При отправке повторного правильного письма после предыдущей ошибки отправляет, но виснет на окне Sending message...
# NOTE  Висело из-за того, что не закрыто окно с предыдущей ошибкой (нормальная ситуация)
# [fixed] После ошибочной отправки не очищается очередь работы (incr, decr)
# [x] Присоединяет выбранный файл к письму (кнопка Attach)
# [x] Выводит список присоединенных к письму файлов (кнопка Parts)

# --------------------------- Окно ответа на письмо -------------------------- #

# [x] Открывается диалог отправки ответа из главного окна (кнопка Reply)
# [x] Добавляет подпись Re:/Fwd: для заголовка письма
# [x] Заголовок Сс заполняется всеми получателями оригинального письма
# [x] Отсылает ответ на письмо (кнопка Send)
# [x] Открывает диалог пересылки письма из главного окна (кнопка Fwd)
# [x] Пересылает письмо (кнопка Send)
