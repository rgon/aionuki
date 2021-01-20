from pynuki import NukiBridge
from functools import partial

toret = []
for x in range(0, 3):
    print(x)

    DiscoveredBridge = partial(NukiBridge, port=x)

    """
    class DiscoveredBridge(NukiBridge):
        def __init__(self, session=None, *args, **kwargs):
            customport = x  # copy first

            print("hello")
            super().__init__(
                session,
                "fakeip",
                *args,
                **kwargs,
            )
            self.port = customport
            print(self.port)
            print("bye")
    """

    toret.append(DiscoveredBridge)

print("testing...")
try:
    print("is the same:", toret[0] is toret[1])

    assert toret[0] is not toret[1]
    for i in range(0, len(toret)):
        print(i)
        thisBridge = toret[i](hostname="none")
        print(thisBridge)
        print(thisBridge.port)
        assert thisBridge.port == i
except Exception as ex:
    print("err", ex)
else:
    print("passed")
