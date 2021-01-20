#!/usr/bin/python
from pynuki import NukiBridge  # , NukiInterface
import aiohttp  #  TODO: remove this dependency
import asyncio


async def main():
    bridges = await NukiBridge.discover()
    print(bridges)

    async with aiohttp.ClientSession() as session:
        br = bridges[0](session, token="kov058")  # tries logging in
        print("Starting the interactive auth procedure.", br)
        # await br.connect()

        if not br.token:
            print("got token:", await br.auth())
        else:
            print("token already set up")

        print(await br.info())
        lock = (await br.locks)[0]

        print(lock)
        await lock.update()
        print(lock.door_sensor_state)
        # await lock.update(True)

        # print("should be entered", await brInst.auth())
        # print(await test)

    print("should be exitted")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())