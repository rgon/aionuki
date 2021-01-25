#!/usr/bin/python
# coding: utf-8

"""
Developed following the Nuki Bridge API version 1.11 specification.

TODO: v1.12 support

Documentation:
https://developer.nuki.io/t/bridge-http-api/26
https://developer.nuki.io/uploads/short-url/5tLp76dEJ1RYfkSUKxFTUSeyJNg.pdf
"""

import logging

import asyncio
import aiohttp

from functools import partial

from . import constants as const
from .device import NukiDevice
from .lock import NukiLock
from .opener import NukiOpener
from .utils import hash_token, logger
from .exceptions import BridgeUninitializedException, InvalidCredentialsException

# Default values
REQUESTS_TIMEOUT = 5


class NukiBridge(object):
    def __init__(
        self,
        hostname,
        port=8080,
        session=None,
        token=None,
        secure=True,
        timeout=REQUESTS_TIMEOUT,
    ):
        self.hostname = hostname
        self.port = port
        self.__api_url = f"http://{hostname}:{port}"
        self.secure = secure
        self.requests_timeout = timeout
        self.auth_timeout = 30  # The bridge times out in 30s https://developer.nuki.io/page/nuki-bridge-http-api-1-12/4/#heading--auth
        self._json = None
        self.token = token

        self.session = session

        self.managedDevices = None  # []

    def __repr__(self):
        return f"<NukiBridge: {self.hostname}:{self.port} (token={self.token})>"

    async def startSession(self):
        self.session = aiohttp.ClientSession()
        await self.session.__aenter__()

    async def endSession(self, type, value, traceback):
        await self.session.__aexit__(type, value, traceback)

    async def __aenter__(self):
        # ttysetattr etc goes here before opening and returning the file object
        await self.startSession()
        return self

    async def __aexit__(self, type, value, traceback):
        # Exception handling here
        await self.endSession(type, value, traceback)

    @staticmethod
    async def discover():
        # Use a sepparate session, doesn't make sense to use the cloud session for local reqs
        async with aiohttp.ClientSession() as discoverSession:
            async with discoverSession.get(
                "https://api.nuki.io/discover/bridges"
            ) as res:
                data = await res.json()
                logger.debug(f"Discovery returned {data}")
                error_code = data.get("errorCode", -9999)
                if error_code != 0:
                    logger.error(f"Discovery failed with error code {error_code}")
                bridges = data.get("bridges")
                if not bridges:
                    logger.warning("No bridge discovered.")
                    return []
                else:
                    toret = []
                    for x in bridges:

                        DiscoveredBridge = partial(
                            NukiBridge, x.get("ip"), port=x.get("port")
                        )

                        toret.append(DiscoveredBridge)
                    return toret

    @property
    def bridgeId(self):
        return f"{self.hostname}:{self.port}"

    # not using token.setter, since this would force caling .info() without await. Using self.connect(token=None) instead
    async def connect(self, token=None):
        if token:
            self.token = token

        # Try to log in if token has been set
        if self.token:
            try:
                await self.info()
                logger.info("Login succeeded.")
                await self.getDevices()
                logger.info("Device list succeeded.")
            except aiohttp.ClientResponseError as err:
                if err.code == 401:
                    logger.error("Could not login with provided credentials")
                    raise InvalidCredentialsException(
                        "Login error. Provided token is invalid."
                    )

    @property
    async def is_hardware_bridge(self):
        info = await self.info()
        return info.get("bridgeType") == const.BRIDGE_TYPE_HW

    async def __rq(self, endpoint, params=None, timeout=None):
        if timeout == None:
            timeout = self.requests_timeout

        if self.session == None:
            await self.startSession()
        elif self.session.closed:
            # await self.endSession()
            await self.startSession()

        url = f"{self.__api_url}/{endpoint}"
        if self.secure:
            get_params = hash_token(self.token)
        else:
            get_params = {"token": self.token}
        if params:
            get_params.update(params)
        # Convert list to string to prevent request from encoding the url params
        # https://stackoverflow.com/a/23497912
        get_params_str = "&".join(f"{k}={v}" for k, v in get_params.items())

        async with self.session.get(
            url,
            params=get_params_str,
            timeout=timeout,
            raise_for_status=True,
        ) as res:
            data = await res.json()
            if "success" in data:
                if not data.get("success"):
                    logger.warning(f"Call failed: {res}")
            return data

    async def auth(self):
        res = await self.__rq("auth")
        self.token = res.get("token", timeout=self.auth_timeout)
        return self.token

    async def config_auth(self, enable):
        return await self.__rq("configAuth", {"enable": 1 if enable else 0})

    async def list(self, device_type=None):
        data = await self.__rq("list")
        if device_type is not None:
            return [x for x in data if x.get("deviceType") == device_type]
        return data

    async def lock_state(self, nuki_id, device_type=const.DEVICE_TYPE_LOCK):
        return await self.__rq(
            "lockState", {"nukiId": nuki_id, "deviceType": device_type}
        )

    async def lock_action(
        self, nuki_id, action, device_type=const.DEVICE_TYPE_LOCK, block=False
    ):
        params = {
            "nukiId": nuki_id,
            "deviceType": device_type,
            "action": action,
            "noWait": 0 if block else 1,
        }
        return await self.__rq("lockAction", params)

    async def unpair(self, nuki_id, device_type=const.DEVICE_TYPE_LOCK):
        return await self.__rq("unpair", {"nukiId": nuki_id, "deviceType": device_type})

    async def info(self):
        # Return cached value
        if self._json:
            return self._json
        data = await self.__rq("info")
        self._json = data
        return data

    # Callback endpoints

    async def callback_get_id_by_url(self, callback_url):
        installedCalbacks = await self.callback_list()

        for i in installedCalbacks["callbacks"]:
            if i["url"] == callback_url:
                return i
        return -1

    async def callback_add(self, callback_url, check_if_exists=True):
        if check_if_exists:
            if await self.callback_get_id_by_url(callback_url) != -1:
                return {"success": True}

        return await self.__rq("callback/add", {"url": callback_url})

    async def callback_list(self):
        return await self.__rq("callback/list")

    async def callback_remove(self, callback_id):
        return await self.__rq("callback/remove", {"id": callback_id})

    async def callback_remove_by_url(self, callback_url):
        foundNumber = await self.callback_get_id_by_url(callback_url)

        if foundNumber != -1:
            return await self.__rq("callback/remove", {"id": foundNumber})
        else:
            return {"success": False}

    async def callback_remove_all(self):
        for i in range(0, 3):
            await self.callback_remove(i)

    async def interpret_callback(self, data):
        # {'deviceType': 0, 'nukiId': 490318788, 'mode': 2, 'state': 3, 'stateName': 'unlocked', 'batteryCritical': False, 'batteryCharging': False, 'batteryChargeState': 70, 'doorsensorState': 3, 'doorsensorStateName': 'door opened'}
        await self.getDeviceFromManagedDevices(data.get("nukiId")).update(
            {k: v for k, v in data.items() if k != "nukiId"}
        )

    # Maintainance endpoints

    async def log(self, offset=0, count=100):
        return await self.__rq("log", {"offset": offset, "count": count})

    async def clear_log(self):
        return await self.__rq("clearlog")

    async def firmware_update(self):
        return await self.__rq("fwupdate")

    async def reboot(self):
        return await self.__rq("reboot")

    async def factory_reset(self):
        return await self.__rq("factoryReset")

    # Shorthand methods

    async def update(self):
        # Invalidate cache
        self._json = None
        return await self.info()

    async def _get_devices(self, device_type=None):
        devices = []
        for l in await self.list(device_type=device_type):
            # lock_data holds the name and nuki id of the lock
            # eg: {'name': 'Home', 'nukiId': 241563832}
            device_data = {k: v for k, v in l.items() if k not in ["lastKnownState"]}
            # state_data holds the last known state of the lock
            # eg: {'batteryCritical': False, 'state': 1, 'stateName': 'locked'}
            state_data = {
                k: v for k, v in l["lastKnownState"].items() if k not in ["timestamp"]
            }

            # Merge lock_data and state_data
            data = {**device_data, **state_data}

            dev_type = device_data.get("deviceType")
            if dev_type == const.DEVICE_TYPE_LOCK:
                dev = NukiLock(self, data)
            elif dev_type == const.DEVICE_TYPE_OPENER:
                dev = NukiOpener(self, data)
            else:
                logger.warning(f"Unknown device type: {dev_type}")
                dev = NukiDevice(self, data)

            devices.append(dev)

        self.managedDevices = devices
        return devices

    async def getDevices(self):
        await self._get_devices()
        return self.managedDevices

    @property
    async def locks(self):
        if self.managedDevices == None:
            raise BridgeUninitializedException
        else:
            devices = []
            for d in self.managedDevices:
                if isinstance(d, NukiLock):
                    devices.append(d)
            return devices

    @property
    async def openers(self):
        if self.managedDevices == None:
            raise BridgeUninitializedException
        else:
            devices = []
            for d in self.managedDevices:
                if isinstance(d, NukiOpener):
                    devices.append(d)
            return devices

    def getDeviceFromManagedDevices(self, nukiId):
        if self.managedDevices == None:
            raise BridgeUninitializedException
        else:
            for d in self.managedDevices:
                if d.nuki_id == nukiId:
                    return d

    async def lock(self, nuki_id, block=False):
        return await self.lock_action(
            nuki_id,
            action=const.ACTION_LOCK_LOCK,
            device_type=const.DEVICE_TYPE_LOCK,
            block=block,
        )

    async def unlock(self, nuki_id, block=False):
        return await self.lock_action(
            nuki_id,
            action=const.ACTION_LOCK_UNLOCK,
            device_type=const.DEVICE_TYPE_LOCK,
            block=block,
        )

    async def lock_n_go(self, nuki_id, unlatch=False, block=False):
        action = const.ACTION_LOCK_LOCK_N_GO
        if unlatch:
            action = const.ACTION_LOCK_LOCK_N_GO_WITH_UNLATCH
        return await self.lock_action(
            nuki_id,
            action=action,
            device_type=const.DEVICE_TYPE_LOCK,
            block=block,
        )

    async def unlatch(self, nuki_id, block=False):
        return await self.lock_action(
            nuki_id,
            action=const.ACTION_LOCK_UNLATCH,
            device_type=const.DEVICE_TYPE_LOCK,
            block=block,
        )

    async def simple_lock(self, nuki_id, device_type=const.DEVICE_TYPE_LOCK):
        return await self.__rq("lock", {"nukiId": nuki_id, "deviceType": device_type})

    async def simple_unlock(self, nuki_id, device_type=const.DEVICE_TYPE_LOCK):
        return await self.__rq("unlock", {"nukiId": nuki_id, "deviceType": device_type})
