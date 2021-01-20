#!/usr/bin/python
from pynuki import NukiBridge  # , NukiInterface
import asyncio


async def main():
    bridges = await NukiBridge.discover()

    async with (bridges[0])(token=None) as br:
        print("Starting the interactive auth procedure.", br)
        await br.connect()

        if not br.token:
            print("got token:", await br.auth())
        else:
            print("token already set up")

        print(await br.info())
        lock = (await br.locks)[0]

        print(lock)
        await lock.update()
        print(lock.door_sensor_state)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())