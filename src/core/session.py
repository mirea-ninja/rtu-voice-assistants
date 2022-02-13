from aiohttp import ClientSession

async def get_session() -> ClientSession:
    return ClientSession()