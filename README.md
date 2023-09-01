# Dashboard MDGT

Запускается как набор микросервисов.

Сервисы:
* service_bot - Асинхронный бот. Парсит данные по запросам и в канал.
* service_organization - Сервис собирает и обновляет данные по премии, отчетам и сотрудникам.
* service_customer - Сервис собирает и обновляет данные по заказчикам.

#### [Схема БД](https://dbdiagram.io/d/64ca18aa02bd1c4a5e1ab27a)

Работает обновление БД через сетевой диск компании!

## Запуск:
1. Создать папку для проекта. Открыть папку в терминале и выполнить:\
    `git init git clone https://github.com/MOSTDORGEOTREST/dashbord.git`

2. Запуск через docker-compose\
    `docker-compose up`
