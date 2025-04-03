import aiohttp
import asyncio
import json

剪辑人员 = '''{"code":200,"msg":"获取成功","data":[{"id":10258,"nickname":"蔡子君"},{"id":10175,"nickname":"陈海湘"},{"id":10218,"nickname":"陈建宏"},{"id":10221,"nickname":"陈诗庆"},{"id":10139,"nickname":"陈晓红"},{"id":10243,"nickname":"陈雪丽"},{"id":10185,"nickname":"邓龙"},{"id":10284,"nickname":"丁金龙"},{"id":10160,"nickname":"丁润忠"},{"id":10206,"nickname":"方泽文"},{"id":10199,"nickname":"冯艳吉"},{"id":10197,"nickname":"龚浩胜"},{"id":10279,"nickname":"何家乐"},{"id":10059,"nickname":"华熙剪辑"},{"id":10285,"nickname":"黄帆贤"},{"id":10267,"nickname":"黄骏"},{"id":10195,"nickname":"黄晓欣"},{"id":10109,"nickname":"黄颖龙"},{"id":10274,"nickname":"黄韵贤"},{"id":10104,"nickname":"纪剑霞"},{"id":10288,"nickname":"李菲艳"},{"id":10178,"nickname":"李玮烨"},{"id":10063,"nickname":"李志明"},{"id":10257,"nickname":"梁浩洛"},{"id":10236,"nickname":"梁普坚"},{"id":10260,"nickname":"廖振言"},{"id":10235,"nickname":"林仕淇"},{"id":10277,"nickname":"刘恺"},{"id":10293,"nickname":"刘善为"},{"id":10289,"nickname":"刘伟艳"},{"id":10266,"nickname":"刘莹"},{"id":10105,"nickname":"吕思齐"},{"id":10220,"nickname":"缪狄"},{"id":10205,"nickname":"聂泽晗"},{"id":10227,"nickname":"潘丽敏"},{"id":10161,"nickname":"彭凯"},{"id":10291,"nickname":"朴雪银"},{"id":10156,"nickname":"沈佳婷"},{"id":10255,"nickname":"唐晓静"},{"id":10076,"nickname":"外部账户"},{"id":10225,"nickname":"王华桂"},{"id":10275,"nickname":"王小欣"},{"id":10292,"nickname":"王韵丽"},{"id":10261,"nickname":"吴东骏"},{"id":10282,"nickname":"吴丰涛"},{"id":10189,"nickname":"吴虹仪"},{"id":10283,"nickname":"吴凯恋"},{"id":10183,"nickname":"夏海湘"},{"id":10280,"nickname":"向眯眯"},{"id":10173,"nickname":"谢昌鑫"},{"id":10046,"nickname":"谢佩婷"},{"id":10184,"nickname":"徐恬"},{"id":10226,"nickname":"许文雯"},{"id":10147,"nickname":"杨鸿强"},{"id":10281,"nickname":"姚瞻衡"},{"id":10222,"nickname":"姚志刚"},{"id":10287,"nickname":"曾择钦"},{"id":10120,"nickname":"詹淑渝"},{"id":10149,"nickname":"张嘉婷"},{"id":10108,"nickname":"张日强"},{"id":10239,"nickname":"张容"},{"id":10204,"nickname":"张茵"},{"id":10234,"nickname":"郑锦丹"},{"id":10179,"nickname":"郑鑫昊"},{"id":10233,"nickname":"周琳婉"},{"id":10196,"nickname":"周旭"},{"id":10253,"nickname":"朱欣婕"}]}'''


async def fetch_material_list(start_date, end_date, limit=20, duration=[], reject="", business_scene=[], editor_uid=[],
                              photographer_uid="", director_uid="", brand_name="", product_name="",material_type="",
                              autoadjust="", first_publish="", high_quality="", low_efficiency="", fission_type="", front_low_efficiency=""
                              ):
    """
    4.0素材库接口
    Args:
        start_date (str): 起始日期，格式为YYYY-MM-DD
        end_date (str): 结束日期，格式为YYYY-MM-DD
        limit : 20
        duration (list): 可选[1-15, 16-30, 31-60, 61-120]
        reject (str): 可选项[-1, 0, 1]
        business_scene (list): 可选项[1]
        editor_uid (list): 可选项[1]
    Returns:
        ToolResult: 包含API响应数据的工具结果
    """
    url = "https://morphlingv4.jcmasz.com/adminapi/Materialv2/materialListQc"

    headers = {
        "Host": "morphlingv4.jcmasz.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJqaWNodWFuZ21laWFvIiwiaWF0IjoxNzQzNDg4MDU0LCJuYmYiOjE3NDM0ODgwNTQsImV4cCI6MTc0NjA4MDA1NCwiZGF0YSI6eyJpZCI6MTAwMDAsInVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6IjMyMjdmMmY5ZTNlZWU5ODNlNjc5YzIxZGI2YjZhMzdjIiwibmlja25hbWUiOiJcdTdjZmJcdTdlZGZcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdGF0dXMiOjEsImNvbnRhY3RfcGhvbmUiOiIxMzQ2Mjg5MDA4NyIsInJvbGUiOm51bGwsIm9ubHkiOm51bGx9fQ.kaOeZq7pBKJZPLTHSEPAfbkZ255IjmnFs_sCSIwOJdc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.475.400 QQBrowser/13.5.6267.400",
        "sec-ch-ua-platform": '"Windows"',
        "Origin": "https://morphlingv4.jcmasz.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "lang=zh-cn; PHPSESSID=cbb31e627d88dc377cda37364c786762"
    }

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
        "reject": "",
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
        "business_scene": business_scene,
        "material_type": material_type,
        "director_uid": director_uid,
        "editor_uid": editor_uid,
        "photographer_uid": photographer_uid,
        "brand_name": brand_name,
        "product_name": product_name,
        "autoadjust": autoadjust,
        "first_publish": first_publish,
        "high_quality": high_quality,
        "low_efficiency": low_efficiency,
        "fission_type": [fission_type],
        "tag_type": 2,
        "tag_mode": 1
    }
    if front_low_efficiency != "":
        payload['front_low_efficiency'] = front_low_efficiency

    print(json.dumps(payload))

    # connector = aiohttp.TCPConnector(verify_ssl=True)

    # proxy = "http://127.0.0.1:8888"
    proxy = None

    # async with aiohttp.ClientSession(connector=connector) as session:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Status Code: {response.status}")
                print("\nResponse Text:")
                response_text = await response.text()
                print(response_text)
                # try:
                #     response_data = await response.json()
                #     # print("\nResponse JSON:")
                #     print(json.dumps(response_data,ensure_ascii=False))
                # except Exception as e:



                return await response.text()

        except aiohttp.ClientError as e:
            print(f"Request failed: {str(e)}")
            return None


async def main():
    try:
        result = await fetch_material_list('2025-03-20', '2025-03-26', 20, duration=[], reject="", business_scene=[], editor_uid=[10206, 10279])
        print("result", result)
        # print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    asyncio.run(main())
