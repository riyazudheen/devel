# Сервис gateway()


## Описание
Сетевая служба `gateway()` является входной точкой для отправки и приема служебных пакетов данных и взаимодействия с другими узлами в сети BitPie.NET. Это своего рода "ворота" через которые проходит весь полезный трафик для клиентского ПО. 

Основные два метода `inbox()` и `outbox()` обрабатывают входящие и исходящие пакеты, подписанные электронной подписью владельца данных. 
Тело пакета так же может быть зашифровано ключом владельца данных, перед тем как будет передано в метод `outbox()`. 

Обработчики событий могут вызывать методы в других сервисах клиентского ПО в момент приема и передачи пакетов через "ворота". 
Сервис `gateway()` так же ведет подсчет полезного трафика с момента запуска ПО и хранит статистику по дняв в подпапках `.bitpie/bandin` и `.bitpie/bandout`.

Экземпляры атоматов `packet_in()` и `packet_out()` создаются в момент приема и передачи служебного пакета соответственно. Они управляют жизненным циклом пакета, позволяют отследить его текщее состояние и корректно отработать дальнейшие действия с ним.


## Зависит от
* [network()](services/service_network.md)


## Влияет на
* [private_messages()](services/service_private_messages.md)
* [p2p_hookups()](services/service_p2p_hookups.md)
* [supplier()](services/service_supplier.md)
* [udp_transport()](services/service_udp_transport.md)
* [tcp_transport()](services/service_tcp_transport.md)
* [identity_propagate()](services/service_identity_propagate.md)


## Настройки сервиса
* services/gateway/enabled - включение/выключение сервиса `gateway()`


## Связанные файлы проекта
* [services/service_gateway.py](services/service_gateway.py)
* [transport/gateway.py](transport/gateway.py)
* [transport/packet_in.py](transport/packet_in.py)
* [transport/packet_out.py](transport/packet_out.py)
* [transport/bandwidth.py](transport/bandwidth.py)
* [transport/callback.py](transport/callback.py)
* [transport/stats.py](transport/stats.py)


## Запуск автоматов
* [packet_in()](transport/packet_in.md)
* [packet_out()](transport/packet_out.md)