#!/usr/bin/python
from pynuki import NukiBridge  # , NukiInterface
import asyncio
from aiohttp import web
import socket

SERVER_PORT = 7123
CALLBACK_ROUTE = "/nuki_test_callback"

"""
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"deviceType": 0, "nukiId": 490318788, "mode": 9, "state": 9, "stateName": "fakestate", "batteryCritical": "false", "batteryCharging": "false", "batteryChargeState": 70, "doorsensorState": 9, "doorsensorStateName": "door opened"}' \
  http://192.168.10.20:7123/nuki_test_callback
"""


def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
        raise Exception
    finally:
        s.close()
    return IP


def getCallbackUrl():
    return f"http://{localIp}:{SERVER_PORT}{CALLBACK_ROUTE}"


localIp = getLocalIp()
callbackUrl = getCallbackUrl()
routes = web.RouteTableDef()

globalbr = None


@routes.post(CALLBACK_ROUTE)
async def hello(request):
    global globalbr
    if globalbr:
        data = await request.json()

        print(data)
        await globalbr.callback(data)
        print((await globalbr.locks)[0].state_name)
        # return web.Response(text="Hello, world")
        return web.Response(text="ok")
    else:
        return web.Response(
            text="err: not ready yet", status=503, reason="Not ready yet."
        )


async def main():
    global globalbr

    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, localIp, SERVER_PORT)
    await site.start()

    print("Server started")

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

        await br.getDevices()
        print("closing")
        await br.session.close()
        print("closed")
        await br.getDevices()

        # Clear pre-existing callbacks
        for i in range(0, 3):
            await br.callback_remove(i)

        await br.callback_add(callbackUrl)
        print(await br.callback_list())

        globalbr = br  # so it can be accessed by the server

    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # sleep forever


loop = asyncio.get_event_loop()
loop.run_until_complete(main())