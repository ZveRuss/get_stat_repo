# get_stat_repo
Скрипт для вывода статистики заданного репозитория Github.

# Назначение скрипта
Скрипт позволяет выгружать данные по заданному URL репозитория

# Описание работы со скриптом
Для работы скрипта требуется установка библиотеки requests.
Чтобы ее установить, необходимо запустить команду pip install -r requirements.txt

Запуск скрипта осуществляется из командной строки с параметрами:
[URL] - URL репозитория Github
[date_begin] - дата, начиная с которой производится анализ (в формате ISO 8601, например, 2020-03-06T12:00:00Z)
[date_end] - дата, по которую производится анализ (в формате ISO 8601, например, 2020-03-06T12:00:00Z)
[branch] - анализируемая ветка

# Пример
python get_repo_info.py --url=https://github.com/WillKoehrsen/Data-Analysis --date_begin=2007-03-06T12:00:00Z --date_end=2020-01-01-01T00:00:00Z --branch=master

Лог ошибок ведется в error.log

Для регулярного запуска можно использовать cron (для *NIX-систем):
Например:
0 */4 * * * /usr/bin/python3 /dir/to/get_stat_repo.py --url=<url> [--date_begin=<date_begin>] [--date_end=<date_end>] [--branch=<branch>]
для запуска скрипта каждые 4 часа.
