import aiohttp
import requests
import json


class CrawlabApi:
    def __init__(self):
        self.Authorization = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3YTZjYWFkMzAyMzNjOTIzNTAyNWM3ZCIsIm5iZiI6MTczODk4NDEyMywidXNlcm5hbWUiOiJhZG1pbiJ9.9xPs8dZ_0QwUh1uL_X-N58XoxsSFvBg6c7PUqSO0k3U'
    async def addspider(self, data):
        spider_name=data['new_config']['spider_name']
        tasktime=data['new_config']['tasktime'][0]
        url = "http://localhost:8080/api/schedules"
        payload = json.dumps({
            "enabled": True,
            "param" : f"-a config=\'{json.dumps(data)}\'",
            "mode": "random",
            "priority": 5,
            "name": spider_name,
            "cron": tasktime,
            "spider_id": "67b2e5026fe6ca3ddb52c5a0",
            "cmd": f"scrapy crawl {spider_name}"
        })
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Authorization': self.Authorization,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:8080',
            'Pragma': 'no-cache',
            'Referer': 'http://localhost:8080/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                return  await response.json()
    async def deletspider(self, data):
        tasktimeid=data["timetaskid"]
        url = f"http://127.0.0.1:8080/api/schedules/{tasktimeid}"

        payload = {}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3YTZjYWFkMzAyMzNjOTIzNTAyNWM3ZCIsIm5iZiI6MTczODk4NDEyMywidXNlcm5hbWUiOiJhZG1pbiJ9.9xPs8dZ_0QwUh1uL_X-N58XoxsSFvBg6c7PUqSO0k3U',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'http://127.0.0.1:8080',
            'Pragma': 'no-cache',
            'Referer': 'http://127.0.0.1:8080/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return "ok"
                else:
                    return "no ok"

