import aiohttp
import asyncio
import json


async def fetch_material_list(start_date: str, end_date: str, limit=10, duration=[], reject=""):
    # URL from the request
    url = 'https://morphlingv4.jcmasz.com/adminapi/Materialv2/materialListQc'

    # Headers from the captured request
    headers = {
        'Host': 'morphlingv4.jcmasz.com',
        'Connection': 'keep-alive',
        'Content-Length': '690',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJqaWNodWFuZ21laWFvIiwiaWF0IjoxNzQyMzU1MTMxLCJuYmYiOjE3NDIzNTUxMzEsImV4cCI6MTc0NDk0NzEzMSwiZGF0YSI6eyJpZCI6MTAwMDAsInVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6IjMyMjdmMmY5ZTNlZWU5ODNlNjc5YzIxZGI2YjZhMzdjIiwibmlja25hbWUiOiJcdTdjZmJcdTdlZGZcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdGF0dXMiOjEsImNvbnRhY3RfcGhvbmUiOiIxMzQ2Mjg5MDA4NyIsInJvbGUiOm51bGwsIm9ubHkiOm51bGx9fQ.brjkr1GutQhndUlp8Ttjopc47n_bzJCcNs0icI9Mfi8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.475.400 QQBrowser/13.5.6267.400',
        'sec-ch-ua-platform': '"Windows"',
        'Origin': 'https://morphlingv4.jcmasz.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'lang=zh-cn; PHPSESSID=cbb31e627d88dc377cda37364c786762'
    }

    # Request payload (JSON body)
    payload = {
        "duration": duration,
        "size": [],
        "page": 1,
        "limit": limit,
        "query": "",
        "date": None,
        "cate_id": "",
        "field": "create_time",
        "order": "",
        "channel": 1,
        "tag": [],
        "reject": reject,
        "area": 0,
        "need_order_field": "stat_cost",
        "need_order_type": "desc",
        "need_field": [
            "click_rate", "convert_cost", "convert_rate", "show_cnt",
            "click_cnt", "convert_cnt", "dy_follow", "total_play",
            "valid_play", "thousand_show_cost", "ad_id_count", "primary_name"
        ],
        "need_date": [start_date, end_date],
        "id": [],
        "business_scene": [],
        "material_type": "",
        "director_uid": "",
        "editor_uid": [],
        "photographer_uid": "",
        "brand_name": "",
        "product_name": "",
        "autoadjust": "",
        "first_publish": "",
        "high_quality": "",
        "low_efficiency": "",
        "fission_type": [],
        "tag_type": 2,
        "tag_mode": 1
    }

    # 创建一个不使用代理的 connector
    connector = aiohttp.TCPConnector(verify_ssl=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            # Print status and response
            print(f'Status: {response.status}')
            return await response.text()


async def main():
    try:
        result = await fetch_material_list('2025-03-26', '2025-03-26', 20)
        print("result", result)
        # print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    asyncio.run(main())