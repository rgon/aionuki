# pynuki

![PyPI](https://img.shields.io/pypi/v/aionuki)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aionuki)
![PyPI - License](https://img.shields.io/pypi/l/aionuki)
![Python Lint](https://github.com/rgon/aionuki/workflows/Python%20Lint/badge.svg)

Asynchronous Python library for interacting with Nuki locks and openers. Forked from [pynuki](https://github.com/pschmitt/pynuki/). Refactored to use aiohttp and asyncio.

Supports automatic bridge discovery using `nuki.io` servers and interactive authentication without manually entering any token.

Supports parsing callbacks and integrating the result in the object's data structure.

## Installation

```bash
pip install -U aionuki
```

## Usage

```python
import asyncio
from aionuki import NukiBridge

async def main():
    bridges = await NukiBridge.discover()

    async with (bridges[0])(token=None) as br:
        print("Starting the interactive auth procedure.", br)

        if not br.token:
            print("Received token:", await br.auth())

        await br.connect()

        lock = (await br.locks)[0]

        await lock.lock()
        await lock.unlock()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

More info in the [examples](examples/) directory.