import re
import aiohttp
import asyncio
from mitmproxy import http

async def fetch_token(session):
    async with session.get("http://38.165.2.248:55555/?token=facai") as response:
        if response.status == 200:
            return await response.text()
        else:
            print("获取新 token 失败，状态码:", response.status)
            return None

async def request(flow: http.HTTPFlow) -> None:
    # 正则表达式匹配目标 URL
    if re.match(r"https://edgeone-api.helloworld88.com/youdao/text\?reqId=[\w]+", flow.request.pretty_url):
        print("URL 匹配成功:", flow.request.pretty_url)
        
        # 使用 aiohttp 异步获取 token
        async with aiohttp.ClientSession() as session:
            new_token = await fetch_token(session)
            if new_token:
                print("获取新 token 成功:", new_token)
                flow.request.headers["token"] = new_token
                print("token 替换成功:", flow.request.headers["token"])
            else:
                print("未能获取新 token")
    else:
        print("URL 不匹配:", flow.request.pretty_url)
