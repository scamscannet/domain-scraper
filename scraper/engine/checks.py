import asyncio

import httpx


async def check_for_http_or_https(url: str):
    raw_url = url.replace("https://", "").replace("http://", "")
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("https://" + raw_url ),
            client.get("http://" + raw_url )
        ]
        results = await asyncio.gather(*tasks)
    if 200 <= results[0].status_code < 400 :
        return "https://" + raw_url
    elif 200 <= results[1].status_code < 400:
        return "http://" + raw_url
    else:
        raise Exception("Unavailable")