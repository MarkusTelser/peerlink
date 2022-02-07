import asyncio
import aiohttp
from time import sleep

async def test():
    print('hello')
    return 0

def add_here(task: asyncio.Task):
    print(task.exception(), task.result())
    print('finished')

async def request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            pokemon = await resp.text()
            print(pokemon)

async def main():
    url = 'https://pokeapi.co/api/v2/pokemon/151'
    asyncio.create_task(request(url))
    print('after')
    task = asyncio.create_task(test())
    task.add_done_callback(add_here)
    i = 0
    while True:
        print("round", i)
        await asyncio.sleep(1)
        i += 1

asyncio.run(main())