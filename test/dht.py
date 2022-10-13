from src.backend.dht.DHT import DHT
import asyncio

async def run():
    dht = DHT()
    asyncio.create_task(DHT.ping("router.utorrent.com", 6881))
    asyncio.create_task(DHT.ping("router.bittorrent.com", 6881))
    asyncio.create_task(DHT.ping("dht.transmissionbt.com", 6881))
    asyncio.create_task(DHT.ping("router.bitcomet.com", 6881))
    asyncio.create_task(DHT.ping("dht.aeltis.com", 6881))
    await asyncio.sleep(1000)


asyncio.run(run())
