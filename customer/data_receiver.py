#!/usr/bin/env python
# data_receiver.py
#
# Copyright (C) 2008-2016 Veselin Penev, http://bitdust.io
#
# This file (data_receiver.py) is part of BitDust Software.
#
# BitDust is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BitDust Software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with BitDust Software.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact us if you have any questions at bitdust.io@gmail.com

"""
.. module:: data_receiver
.. role:: red

BitDust data_receiver() Automat

EVENTS:
    * :red:`init`
    * :red:`input-stream-closed`
    * :red:`input-stream-opened`
    * :red:`shutdown`
"""

#------------------------------------------------------------------------------

from __future__ import absolute_import

#------------------------------------------------------------------------------

_Debug = True
_DebugLevel = 14

#------------------------------------------------------------------------------

from automats import automat

from transport import callback

#------------------------------------------------------------------------------

_DataReceiver = None

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    """
    Access method to interact with the state machine.
    """
    global _DataReceiver
    if event is None and arg is None:
        return _DataReceiver
    if _DataReceiver is None:
        _DataReceiver = DataReceiver(publish_events=True, log_events=_Debug, debug_level=_DebugLevel)
    if event is not None:
        _DataReceiver.automat(event, arg)
    return _DataReceiver

#------------------------------------------------------------------------------

class DataReceiver(automat.Automat):
    """
    This class implements all the functionality of ``data_receiver()`` state machine.
    """

    def __init__(self, debug_level=0, log_events=False, publish_events=False, **kwargs):
        """
        Builds `data_receiver()` state machine.
        """
        super(DataReceiver, self).__init__(
            name="data_receiver",
            state="AT_STARTUP",
            debug_level=debug_level,
            log_events=log_events,
            publish_events=publish_events,
            **kwargs
        )

    def A(self, event, arg):
        """
        The state machine code, generated using `visio2python <http://bitdust.io/visio2python/>`_ tool.
        """
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.state = 'READY'
                self.doInit(arg)
                self.StreamsCounter=0
        #---READY---
        elif self.state == 'READY':
            if event == 'input-stream-opened':
                self.state = 'RECEIVING'
                self.StreamsCounter+=1
            elif event == 'shutdown':
                self.state = 'CLOSE'
                self.doDestroyMe(arg)
        #---RECEIVING---
        elif self.state == 'RECEIVING':
            if event == 'input-stream-closed' and self.StreamsCounter>1:
                self.StreamsCounter-=1
            elif event == 'input-stream-closed' and self.StreamsCounter==1:
                self.state = 'READY'
                self.StreamsCounter=0
            elif event == 'input-stream-opened':
                self.StreamsCounter+=1
            elif event == 'shutdown':
                self.state = 'CLOSE'
                self.doDestroyMe(arg)
        #---CLOSE---
        elif self.state == 'CLOSE':
            pass
        return None

    def doInit(self, arg):
        """
        Action method.
        """
        callback.add_begin_file_receiving_callback(self._on_begin_file_receiving)
        callback.add_finish_file_receiving_callback(self._on_finish_file_receiving)

    def doDestroyMe(self, arg):
        """
        Action method.
        """
        callback.remove_begin_file_receiving_callback(self._on_begin_file_receiving)
        self.destroy()
        global _DataReceiver
        del _DataReceiver
        _DataReceiver = None

    def _on_begin_file_receiving(self, pkt_in):
        self.event('input-stream-opened', pkt_in)

    def _on_finish_file_receiving(self, pkt_in, data):
        self.event('input-stream-closed', (pkt_in, data, ))
