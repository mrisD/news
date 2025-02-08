import requests
import json


class CrawlabApi:
    def __init__(self):
        self.Authorization = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3YTZjYWFkMzAyMzNjOTIzNTAyNWM3ZCIsIm5iZiI6MTczODk4NDEyMywidXNlcm5hbWUiOiJhZG1pbiJ9.9xPs8dZ_0QwUh1uL_X-N58XoxsSFvBg6c7PUqSO0k3U'
    def addspider(self, data):
        spidername=data['new_config']['spidername']
        tasktime=data['new_config']['tasktime'][0]
        url = "http://localhost:8080/api/schedules"
        payload = json.dumps({
            "enabled": True,
            "mode": "random",
            "priority": 5,
            "name": spidername,
            "cron": tasktime,
            "spider_id": "67a6cad730233c9235025df3",
            "cmd": f"scrapy crawl {spidername}"
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

        response = requests.request("POST", url, headers=headers, data=payload)

        return response
