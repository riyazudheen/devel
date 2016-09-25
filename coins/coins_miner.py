#!/usr/bin/env python
#coins_miner.py
#
# Copyright (C) 2008-2016 Veselin Penev, http://bitdust.io
#
# This file (coins_miner.py) is part of BitDust Software.
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
.. module:: coins_miner
.. role:: red

BitDust coins_miner() Automat

EVENTS:
    * :red:`accountant-connected`
    * :red:`coin-confirmed`
    * :red:`coin-mined`
    * :red:`coin-rejected`
    * :red:`init`
    * :red:`lookup-failed`
    * :red:`new-data-received`
    * :red:`shutdown`
    * :red:`start`
    * :red:`stop`
    * :red:`timer-2min`
"""

#------------------------------------------------------------------------------ 

_Debug = True
_DebugLevel = 6

#------------------------------------------------------------------------------ 

import random
import string
import hashlib
import json

from twisted.internet import reactor
from twisted.internet import threads

#------------------------------------------------------------------------------ 

from logs import lg

from automats import automat

from userid import my_id

from lib import utime

from p2p import commands
from p2p import p2p_service

from transport import callback

from coins import local_storage

#------------------------------------------------------------------------------ 

_CoinsMiner = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    """
    Access method to interact with the state machine.
    """
    global _CoinsMiner
    if event is None and arg is None:
        return _CoinsMiner
    if _CoinsMiner is None:
        # set automat name and starting state here
        _CoinsMiner = CoinsMiner('coins_miner', 'AT_STARTUP', _DebugLevel, _Debug)
    if event is not None:
        _CoinsMiner.automat(event, arg)
    return _CoinsMiner

def Destroy():
    """
    Destroy the state machine and remove the instance from memory. 
    """
    global _CoinsMiner
    if _CoinsMiner is None:
        return
    _CoinsMiner.destroy()
    del _CoinsMiner
    _CoinsMiner = None

#------------------------------------------------------------------------------ 

class CoinsMiner(automat.Automat):
    """
    This class implements all the functionality of the ``coins_miner()`` state machine.
    """

    timers = {
        'timer-2min': (120, ['ACCOUNTANTS?']),
        }

    def init(self):
        """
        Method to initialize additional variables and flags
        at creation phase of coins_miner() machine.
        """
        self.connected_accountants = []
        self.min_accountants_connected = 3 # TODO: read from settings
        self.max_accountants_connected = 5 # TODO: read from settings
        self.input_data = []
        self.max_mining_counts = 10**8 # TODO: read from settings
        self.max_mining_seconds = 60*3 # TODO: read from settings
        self.simplification = 2
        self.starter_length = 10 
        self.starter_limit = 99999  
        self.mining_started = None
        self.mining_counts = 0

    def A(self, event, arg):
        """
        The state machine code, generated using `visio2python <http://bitdust.io/visio2python/>`_ tool.
        """
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.state = 'STOPPED'
                self.doInit(arg)
        elif self.state == 'READY':
            if event == 'stop':
                self.state = 'STOPPED'
            elif event == 'shutdown':
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'new-data-received' and self.isDecideOK(arg):
                self.state = 'MINING'
                self.doStartMining(arg)
            elif event == 'new-data-received' and not self.isDecideOK(arg):
                self.doSendFail(arg)
        elif self.state == 'MINING':
            if event == 'stop':
                self.state = 'STOPPED'
                self.doStopMining(arg)
            elif event == 'coin-mined':
                self.state = 'PUBLISH_COIN'
                self.doSendCoinToAccountants(arg)
            elif event == 'shutdown':
                self.state = 'CLOSED'
                self.doStopMining(arg)
                self.doDestroyMe(arg)
            elif event == 'new-data-received':
                self.doPushInputData(arg)
        elif self.state == 'STOPPED':
            if event == 'start':
                self.state = 'ACCOUNTANTS?'
                self.doLookupAccountants(arg)
            elif event == 'shutdown':
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
        elif self.state == 'PUBLISH_COIN':
            if event == 'stop':
                self.state = 'STOPPED'
            elif event == 'coin-confirmed' and self.isAllConfirmed(arg):
                self.state = 'READY'
                self.doSendAck(arg)
                self.doCheckInputData(arg)
            elif event == 'shutdown':
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'coin-rejected' and not self.isDecideOK(arg):
                self.state = 'READY'
                self.doSendFail(arg)
            elif event == 'coin-rejected' and self.isDecideOK(arg):
                self.state = 'MINING'
                self.doContinueMining(arg)
            elif event == 'new-data-received':
                self.doPushInputData(arg)
        elif self.state == 'ACCOUNTANTS?':
            if event == 'stop' or event == 'timer-2min' or ( event == 'lookup-failed' and not self.isAnyAccountants(arg) ):
                self.state = 'STOPPED'
            elif event == 'accountant-connected' and not self.isMoreNeeded(arg):
                self.state = 'READY'
                self.doAddAccountant(arg)
                self.doLookupAccountants(arg)
            elif event == 'accountant-connected' and self.isMoreNeeded(arg):
                self.doAddAccountant(arg)
                self.doLookupAccountants(arg)
            elif event == 'stop':
                self.state = 'CLOSED'
                self.doStopMining(arg)
            elif event == 'new-data-received':
                self.doPushInputData(arg)
        elif self.state == 'CLOSED':
            pass
        return None

    def isAnyAccountants(self, arg):
        """
        Condition method.
        """
        return len(self.connected_accountants) > 0

    def isMoreNeeded(self, arg):
        """
        Condition method.
        """
        return len(self.connected_accountants) < self.max_accountants_connected

    def isDecideOK(self, arg):
        """
        Condition method.
        """
        # TODO:
        return True

    def isAllConfirmed(self, arg):
        """
        Condition method.
        """
        # TODO:
        return True

    def doInit(self, arg):
        """
        Action method.
        """
        callback.append_inbox_callback(self._on_inbox_packet)

    def doLookupAccountants(self, arg):
        """
        Action method.
        """
        if len(self.connected_accountants) >= self.max_accountants_connected:
            self.automat('accountant-connected', self.connected_accountants[0])
            return
        from coins import accountants_finder
        accountants_finder.A('start', (self.automat, 'read'))
    
    def doPushInputData(self, arg):
        """
        Action method.
        """
        self.input_data.append(arg)

    def doPullInputData(self, arg):
        """
        Action method.
        """
        if len(self.input_data) > 0:
            self.automat('new-data-received', self.input_data.pop(0))

    def doStartMining(self, arg):
        """
        Action method.
        """
        self.mining_started = utime.get_sec1970()
        self._start(arg, '')

    def doStopMining(self, arg):
        """
        Action method.
        """

    def doSendCoinToAccountants(self, arg):
        """
        Action method.
        """

    def doAddAccountant(self, arg):
        """
        Action method.
        """

    def doContinueMining(self, arg):
        """
        Action method.
        """

    def doSendAck(self, arg):
        """
        Action method.
        """

    def doSendFail(self, arg):
        """
        Action method.
        """

    def doDestroyMe(self, arg):
        """
        Action method.
        """
        callback.remove_inbox_callback(self._on_inbox_packet)
        automat.objects().pop(self.index)
        global _CoinsMiner
        del _CoinsMiner
        _CoinsMiner = None

    #------------------------------------------------------------------------------ 

    def _on_inbox_packet(self, newpacket, info, status, error_message):
        if status != 'finished':
            return False
        if newpacket.Command == commands.Coin():
            coins_list = local_storage.read_coins_from_packet(newpacket)
            if not coins_list:
                # p2p_service.SendFail(newpacket, 'failed to read coins from packet')
                return False
            new_coins = []
            for acoin in coins_list:
                if local_storage.validate_coin(acoin):
                    continue
                new_coins.append(acoin)
            if not new_coins:
                # p2p_service.SendFail(newpacket, 'did not received any coins to mine')
                return False
            for coin in new_coins:
                self.automat('new-coin-received', coin)
            return True
        return False        

    def _stop_marker(self):
        if self.state != 'MINING':
            return True
        if self.mining_counts >= self.max_mining_counts:
            return True
        if utime.get_sec1970() - self.mining_started > self.max_seconds:
            return True
        self.mining_counts += 1
        return False

    def _build_starter(self, length):
        return (''.join(
            [random.choice(string.uppercase+string.lowercase+string.digits)
                for _ in xrange(length)])) + '_'    
    
    def _build_hash(self, payload):
        return hashlib.sha1(payload).hexdigest()
    
    def _get_hash_complexity(self, hexdigest, simplification):
        complexity = 0
        while complexity < len(hexdigest):
            if int(hexdigest[complexity], 16) < simplification:
                complexity += 1
            else:
                break
        return complexity
    
    def _get_hash_difficulty(self, hexdigest, simplification):
        difficulty = 0
        while True:
            ok = False
            for simpl in xrange(simplification):
                if hexdigest.startswith(str(simpl)*difficulty):
                    ok = True
                    break
            if ok:
                difficulty += 1
            else:
                break
        return difficulty - 1 
    
    def _run(self, data, difficulty, simplification, starter_length, starter_limit):
        data_dump = json.dumps(data)
        starter = self._build_starter(starter_length)
        on = 0
        while True:
            if self._stop_marker():
                return None
            check = starter + str(on)
            if data is not None:
                check += data_dump
            hexdigest = self._build_hash(check)
            if difficulty != self._get_hash_complexity(hexdigest, simplification):
                on += 1
                if on > starter_limit:
                    starter = self._build_starter(starter_length)
                    on = 0
                continue
            return {
                "starter": starter+str(on), 
                "hash": hexdigest,
                "tm": utime.utcnow_to_sec1970(),
                "data": data,
            }
        
    def _start(self, data, prev_hash):
        data['prev'] = prev_hash
        data['miner'] = my_id.getLocalID()
        difficulty = self._get_hash_difficulty(prev_hash)
        complexity = self._get_hash_complexity(prev_hash)
        if difficulty == complexity:
            complexity += 1
            if _Debug:
                lg.out(_DebugLevel, 'coins_miner.found golden coin, step up complexity: %s' % complexity)
        return threads.deferToThread(self._run, data, difficulty,
                                     self.simplification, self.starter_length, self.starter_limit)