# Сервис data_motion()


## Описание
Сетевая служба `data_motion()` ответственна за скачивание/загрузку пользовательских данных
с/на машины хранителей. 

Поддерживаются две отдельные очереди пакетов для приема/передачи данных для каждого хранителя,
а так же может быть установлено колличество одновременных трансферов на отдельного хранителя.

Подготовленные для отправки файлы предварительно сохраняются в подпапке `.bitpie/backups/`,
откуда их забирают сетевые транспортные протоколы и запускают трансфер на заданный узел в сети BitPie.NET.

При старте сервиса создается экземпляр автомата `data_sender()`, он подготавливает список файлов
для передачи на хранителей и помещает их в исходящую очередь пакетов.

При отключении службы `data_motion()` станет невозможно передать или получить данные с других узлов в сети
и будут отключены сервисы нижних уровней реализующие распределенное хранение данных.


## Зависит от
* [customer()](services/service_customer.md)


## Влияет на
* [rebuilding()](services/service_rebuilding.md)
* [backup_db()](services/service_backup_db.md)


## Запуск автоматов
* [data_sender()](customer/data_sender.md)


## Настройки сервиса
* services/data-motion/enabled - включение/выключение сервиса `data_motion()`


## Связанные файлы проекта
* [services/service_data_motion.py](services/service_data_motion.py)


