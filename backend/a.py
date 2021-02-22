from aiohttp import ClientSession
import aiohttp
import asyncio

async def conn(ws=None):
    session = ClientSession()
    ws = await session.ws_connect('http://127.0.0.1:4200/ws/100') if not ws else ws
    async for msg in ws:
        print(msg)

loop = asyncio.new_event_loop()
loop.run_until_complete(conn())