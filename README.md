## Описание

Скрипт для проверки [страницы](http://www.itmm.unn.ru/studentam/raspisanie/) расписания ННГУ ИТММ на изменения.

Найдя изменения отправляет их email-сообщением по указанному адресу.

В сообщении содержатся:
* данные о том, что изменено (текст на странице и/или файл расписания);
* файл расписания (если был изменён);
* дата последнего изменения файла расписания;
* ссылки на страницу и файл расписания на сайте ИТММ.

### Пример сообщения

![Пример сообщения](example.png?raw=true "Пример сообщения")

## Использование

Требует для работы:
* Python версии 3.2 и выше;
* функции из [mail](https://github.com/rybval/mail);
* локальный SMTP-сервер.

Рекомендуется использовать в связке с [cron](https://ru.wikipedia.org/wiki/Cron).

Запуск конструкцией вида:

``itmm_schedule_checker.py <from-email> <to-email>``



