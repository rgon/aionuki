#!/usr/bin/python
import asyncio
import aiohttp
from aionuki import NukiBridge


async def main():
    bridges = await NukiBridge.discover()
    print(bridges)

    async with aiohttp.ClientSession() as session:
        br = (bridges[0])(session=session, token=None)
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