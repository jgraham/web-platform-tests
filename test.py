import asyncio
import re
import subprocess
import sys

import requests

from tools import localpaths

import webdriver

async def read_firefox(proc, future):
    url_re = re.compile(".*WebDriver BiDi listening on ([^ ]*)")
    while True:
        line = await proc.stdout.readline()
        if line == b'':
            break
        line = line.decode("utf-8", "replace")
        if not future.done():
            m = url_re.match(line)
            if m:
                url = m.groups(1)[0]
                print("Got BiDi URL %s" % url)
                url = url.strip()
                url = url.replace("ws://", "")
                future.set_result(url)
        else:
            if "BiDi" in line or "RemoteAgent" in line:
                print(line)
    print("No more output")


async def run_bidi_session(loop, url):
    print("Starting session using url %s" % url)
    caps = requests.post("http://%s/session" % url, json={"capabilities": {"alwaysMatch": {"websocketUrl": True}}}).json()
    async with webdriver.bidi.BidiSession("ws://%s/" % url, caps, session_id=caps["sessionId"]) as session:
        test = webdriver.bidi.client.Test(session)
        result = await test.test_method(example="data")
        print("Result:", result)


async def main():
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    print("Starting Gecko")
    proc = await asyncio.create_subprocess_exec(
        sys.argv[1], "--remote-debugging-port",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)

    fx_task = asyncio.create_task(read_firefox(proc, future))
    try:
        url = await future

        await loop.create_task(run_bidi_session(loop, url))
    finally:
        print("Killing process")
        proc.terminate()
        await proc.wait()
        await fx_task


if __name__ == "__main__":
    asyncio.run(main())
