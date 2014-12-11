# Сервис employer()


## Описание
Сервис `employer()` это один из ключевых элементов клиентского ПО BitPie.NET, который обеспечивает
возможность распределенного хранения данных на многих узлах в сети.

При старте службы, создается экземпляр автомата `fire_hire()`, он производит найм и увольнение хранителей 
для пользователя. Программа BitPie.NET должна непрерывно работать на их машинах, а служба `supplier()`
позволяет им предоставить часть своих жестких дисков и создает приватное и распрелеленное 
файло-хранилище для самого пользователя. 

Автомат `fire_hire()` производит поиск новых и замену существующих хранителей - его задача поддерживать 
общую максимальную доступность и работоспособность всего набора хранителей в каждый момент времени.

Подбор новых хранителей производится случайным образом, путем выбора произвольного узла через DHT сеть
и запрос услуги хранения данных. Этим управляет автомат `supplier_finder()`, экземпляр которого создается 
и запускается для выбора нового хранителя.


## Зависит от
* [customer()](services/service_customer.md)


## Влияет на
* [backups()](services/service_backups.md)


## Запуск автоматов
* [fire_hire()](customer/fire_hire.md)
* [supplier_finder()](customer/supplier_finder.md)


## Настройки сервиса
* services/fire-hire/enabled - включение/выключение сервиса `employer()`


## Связанные файлы проекта
* [services/service_fire_hire.py](services/service_fire_hire.py)
* [customer/fire_hire.py](customer/fire_hire.py)
* [customer/supplier_finder.py](customer/supplier_finder.py)

