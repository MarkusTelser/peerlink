import asyncio

async def ttask():
    print('do sometthing')

async def run():
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    t = asyncio.create_task(ttask()) 
    await t

asyncio.run(run())