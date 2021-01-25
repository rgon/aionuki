#!/usr/bin/python
import asyncio
from aionuki import NukiBridge


async def main():
    bridges = await NukiBridge.discover()

    async with (bridges[0])(token=None) as br:
        print("Starting the interactive auth procedure.", br)

        if not br.token:
            print("Received token:", await br.auth())
        else:
            print("Token already set.")

        await br.connect()

        print(await br.info())
        lock = (await br.locks)[0]

        print(lock)
        await lock.update()
        print(lock.door_sensor_state)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())