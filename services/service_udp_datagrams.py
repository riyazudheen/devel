#!/usr/bin/python
#service_udp_datagrams.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: service_udp_datagrams

"""

from services.local_service import LocalService

def create_service():
    return UDPDatagramsService()
    
class UDPDatagramsService(LocalService):
    
    service_name = 'service_udp_datagrams'
    config_path = 'services/udp-datagrams/enabled'
    
    def dependent_on(self):
        return ['service_network',
                ]
    
    def start(self):
        from lib import udp
        from lib import settings
        from lib.config import conf
        udp_port = settings.getUDPPort()
        if not udp.proto(udp_port):
            udp.listen(udp_port)
        conf().addCallback('services/udp-datagrams/udp-port', self.on_udp_port_modified)
        return True
    
    def stop(self):
        from lib import udp
        from lib import settings
        from lib.config import conf
        udp_port = settings.getUDPPort()
        if udp.proto(udp_port):
            udp.close(udp_port)
        conf().removeCallback('services/udp-datagrams/udp-port')
        return True
    
    def on_udp_port_modified(self, path, value, oldvalue, result):
        from p2p import network_connector
        network_connector.A('reconnect')

    