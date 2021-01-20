# coding: utf-8

from . import constants as const
from .device import NukiDevice
from .utils import logger


class NukiOpener(NukiDevice):
    @property
    def is_rto_activated(self):
        return self.state == const.STATE_OPENER_RTO_ACTIVE

    @property
    def ring_action_timestamp(self):
        return self._json.get("ringactionTimestamp")

    @property
    def ring_action_state(self):
        return self._json.get("ringactionState")

    async def activate_rto(self, block=False):
        return await self._bridge.lock_action(
            nuki_id=self.nuki_id,
            action=const.ACTION_OPENER_ACTIVATE_RTO,
            device_type=self.device_type,
            block=block,
        )

    async def deactivate_rto(self, block=False):
        return await self._bridge.lock_action(
            nuki_id=self.nuki_id,
            action=const.ACTION_OPENER_DEACTIVATE_RTO,
            device_type=self.device_type,
            block=block,
        )

    async def electric_strike_actuation(self, block=False):
        return await self._bridge.lock_action(
            nuki_id=self.nuki_id,
            action=const.ACTION_OPENER_ELECTRIC_STRIKE_ACTUATION,
            device_type=self.device_type,
            block=block,
        )

    async def activate_continuous_mode(self, block=False):
        return await self._bridge.lock_action(
            nuki_id=self.nuki_id,
            action=const.ACTION_OPENER_ACTIVATE_CONTINUOUS,
            device_type=self.device_type,
            block=block,
        )

    async def deactivate_continuous_mode(self, block=False):
        return await self._bridge.lock_action(
            nuki_id=self.nuki_id,
            action=const.ACTION_OPENER_DEACTIVATE_CONTINUOUS,
            device_type=self.device_type,
            block=block,
        )
