import requests
import asyncio

from tools import localpaths

import webdriver

async def main():
    caps = requests.post("http://localhost:9222/session", json={"capabilities": {"alwaysMatch": {"websocketUrl": True}}}).json()
    async with webdriver.bidi.BidiSession("ws://localhost:9222/", caps, session_id=caps["sessionId"]) as session:
        resp = await session.session.test({"example": "data"})
        print(await resp)

asyncio.get_event_loop().run_until_complete(main())
