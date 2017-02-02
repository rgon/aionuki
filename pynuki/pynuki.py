#!/usr/bin/python
# coding: utf-8

'''
Based on the Bridge API version 1.5

Documentation:
https://nuki.io/wp-content/uploads/2016/04/Bridge-API-v1.5.pdf
'''

import requests
import logging


logger = logging.getLogger(__name__)


LOCK_STATES = {
    'UNCALIBRATED': 0,
    'LOCKED': 1,
    'UNLOCKING': 2,
    'UNLOCKED': 3,
    'LOCKING': 4,
    'UNLATCHED': 5,
    'UNLOCKED_LOCK_N_GO': 6,
    'UNLATCHING': 7,
    'MOTOR BLOCKED': 254,
    'UNDEFINED': 255
}

LOCK_ACTIONS = {
    'UNLOCK': 1,
    'LOCK': 2,
    'UNLATCH': 3,
    'LOCK_N_GO': 4,
    'LOCK_N_GO_WITH_UNLATCH': 5
}


class NukiLock(object):
    def __init__(self, bridge, json):
        self._bridge = bridge
        self._json = json

    @property
    def name(self):
        return self._json.get('name', None)

    @property
    def nuki_id(self):
        return self._json.get('nukiId', None)

    @property
    def battery_critical(self):
        return self._json.get('batteryCritical', None)

    @property
    def state(self):
        return self._json.get('state', None)

    @property
    def state_name(self):
        return self._json.get('stateName', None)

    def lock(self, block=False):
        return self._bridge.lock(nuki_id=self.nuki_id, block=block)

    def unlock(self, block=False):
        return self._bridge.unlock(nuki_id=self.nuki_id, block=block)

    def update(self):
        data = self._bridge.lock_state(self.nuki_id)
        self._json.update({k:v for k,v in data.items() if k != 'success'})

    def __repr__(self):
        return '<NukiLock: {}>'.format(self._json)


class NukiBridge(object):
    def __init__(self, hostname, token, port=8080):
        self.hostname = hostname
        self.token = token
        self.port = port
        self.__api_url = 'http://{}:{}'.format(hostname, port)

    def __rq(self, endpoint, params=None):
        url = '{}/{}'.format(self.__api_url, endpoint)
        get_params = {'token': self.token}
        if params:
            get_params.update(params)
        result = requests.get(url, params=get_params)
        result.raise_for_status()
        return result.json()

    def list(self):
        return self.__rq('list')

    def lock_state(self, nuki_id):
        return self.__rq('lockState', {'nukiId': nuki_id})

    def lock_action(self, nuki_id, action, block=False):
        params = {
            'nukiId': nuki_id,
            'action': action,
            'noWait': 0 if block else 1
        }
        return self.__rq('lockAction', params)

    def unpair(self, nuki_id):
        return self.__rq('unpair', {'nukiId': nuki_id})

    def info(self):
        return self.__rq('info')

    # Callback endpoints

    def callback_add(self, callback_url):
        return self.__rq('callback/add', {'url': callback_url})

    def callback_list(self):
        return self.__rq('callback/list')

    def callback_remove(self, callback_url):
        return self.__rq('callback/remove', {'url': callback_url})

    # Maintainance endpoints

    def log(self, offset=0, count=100):
        return self.__rq('log', {'offset': offset, 'count': count})

    def clear_log(self):
        return self.__rq('clearlog')

    def firmware_update(self):
        return self.__rq('fwupdate')

    def reboot(self):
        return self.__rq('reboot')

    def factory_reset(self):
        return self.__rq('factoryReset')

    # Shorthand methods

    @property
    def locks(self):
        return [NukiLock(self, l) for l in self.list()]

    def lock(self, nuki_id, block=False):
        return self.lock_action(
            nuki_id, action=LOCK_ACTIONS['LOCK'], block=block
        )

    def unlock(self, nuki_id, block=False):
        return self.lock_action(
            nuki_id, action=LOCK_ACTIONS['UNLOCK'], block=block
        )