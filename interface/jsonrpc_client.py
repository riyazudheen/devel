#!/usr/bin/python
#jsonrpc_client.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: jsonrpc_client
"""


if __name__ == '__main__':
    import sys, os.path as _p
    sys.path.insert(0, _p.abspath(_p.join(_p.dirname(_p.abspath(sys.argv[0])), '..')))

from twisted.internet import reactor

from main import settings

from lib.fastjsonrpc.client import Proxy

#------------------------------------------------------------------------------ 

def output(value):
    print value
    reactor.stop()

proxy = Proxy('http://localhost:%d' % settings.DefaultJsonRPCPort())
proxy.callRemote('stop').addBoth(output)
reactor.run()
