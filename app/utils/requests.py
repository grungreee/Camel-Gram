import aiohttp
import app.settings
from aiohttp import ClientResponse


async def make_request(endpoint: str, data: dict) -> ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{app.settings.url}/{endpoint}", json=data) as response:
            return response.status, await response.json()
