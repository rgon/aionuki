# coding: utf-8

from . import constants as const
from .device import NukiDevice
from .utils import logger


class NukiLock(NukiDevice):
    @property
    def is_locked(self):
        # Return None if unknown
        # https://github.com/home-assistant/core/blob/dev/homeassistant/components/lock/__init__.py
        if self.state == const.STATE_LOCK_LOCKED:
            return True
        elif (
            self.state == const.STATE_LOCK_UNLOCKED
            or self.state == const.STATE_LOCK_UNLOCKED_LOCK_N_GO
        ):
            return False
        else:
            return None

    @property
    def is_open(self):
        if self.door_sensor_state == const.STATE_DOORSENSOR_OPENED:
            return True
        elif self.door_sensor_state == const.STATE_DOORSENSOR_CLOSED:
            return False
        else:
            return None

    @property
    def is_lockngo_in_progress(self):
        return self.state == const.STATE_LOCK_UNLOCKED_LOCK_N_GO

    @property
    def is_door_sensor_activated(self):
        # Nuki v1 locks don't have a door sensor, therefore the
        # door_sensor_state will is unset for them.
        if (
            not self.door_sensor_state
            or self.door_sensor_state == const.STATE_DOORSENSOR_UNKNOWN
        ):
            return
        return self.door_sensor_state != const.STATE_DOORSENSOR_DEACTIVATED

    @property
    def door_sensor_state(self):
        return self._json.get("doorsensorState")

    @property
    def door_sensor_state_name(self):
        return self._json.get("doorsensorStateName")

    @property
    def battery_charge(self):
        return self._json.get("batteryChargeState")

    @property
    def battery_critical_keypad(self):
        return self._json.get("keypadBatteryCritical")

    async def lock(self, block=False):
        return await self._bridge.lock(nuki_id=self.nuki_id, block=block)

    async def unlock(self, block=False):
        return await self._bridge.unlock(nuki_id=self.nuki_id, block=block)

    async def lock_n_go(self, unlatch=False, block=False):
        return await self._bridge.lock_n_go(
            nuki_id=self.nuki_id, unlatch=unlatch, block=block
        )

    async def unlatch(self, block=False):
        return await self._bridge.unlatch(nuki_id=self.nuki_id, block=block)
