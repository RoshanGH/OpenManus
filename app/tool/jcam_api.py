import os
import traceback

import aiohttp
import json
from typing import Dict, Any, Optional

from app.tool.base import BaseTool, ToolResult
from app.tool.v4_api import *

class JcamApiTool(BaseTool):
    name: str = "jcma_api"
    description: str = """
    请求JCMA公司API并获取指定日期范围内的数据。
    该工具用于获取JCMA公司的视频素材信息，包括编导、摄影师、剪辑师等相关数据。
    当用户询问关于JCMA公司数据、编导数据统计、素材分析等问题时，应使用此工具获取原始数据。
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "(必需) 起始日期，格式为YYYY-MM-DD",
            },
            "end_date": {
                "type": "string",
                "description": "(必需) 结束日期，格式为YYYY-MM-DD",
            },
            "duration": {
                "type": "string",
                "description": "(非必需) 视频时长区域，格式为1-15, 可选项[1-15, 16-30, 31-60, 60]   例如: 31-60",
            },
            "reject": {
                "type": "string",
                "description": "(非必需) 视频卡审状态，格式为-1=不做筛选, 0=未卡审, 1=卡审, 可选项[-1, 0, 1]    例如: 0",
            },
            "business_scene": {
                "type": "string",
                "description": "(非必需) 业务场景，格式为1=短视频原创, 2=短视频混剪, 3=直播素材, 4=直播直投, 5=短视频, 6=直播. 可多选[1, 2, 3, 4, 5]   例如: [1, 2]",
            },
            "editor_uid": {
                "type": "string",
                "description": f"(非必需) 剪辑人员，可供选择的数据{剪辑人员}   例如: [10206, 10279]",
            },
            "photographer_uid": {
                "type": "string",
                "description": f"(非必需) 拍摄人员，可供选择的数据{剪辑人员}   例如: 10226",
            },
            "director_uid": {
                "type": "string",
                "description": f"(非必需) 编导人员，可供选择的数据{剪辑人员}   例如: 10226",
            },
            "brand_name": {
                "type": "string",
                "description": f"(非必需) 品牌名称,   例如: 滴露",
            },
            "product_name": {
                "type": "string",
                "description": f"(非必需) 产品名称,   例如: 滴露消毒液",
            },
            "material_type": {
                "type": "string",
                "description": f"(非必需) 素材来源,   可供选择的数据:自制=1、外部=2,     例如: 1",
            },
            "autoadjust": {
                "type": "string",
                "description": f"(非必需) 微调状态,   可供选择的数据:未微调=0、已微调=1,     例如: 1",
            },
            "first_publish": {
                "type": "string",
                "description": f"(非必需) 首发状态,   可供选择的数据:不是首发=0、是首发=1,     例如: 1",
            },
            "high_quality": {
                "type": "string",
                "description": f"(非必需) 优质状态,   可供选择的数据:不是优质=0、是优质=1,     例如: 1",
            },
            "low_efficiency": {
                "type": "string",
                "description": f"(非必需) 低效状态,   可供选择的数据:不是低效=0、是低效=1,     例如: 1",
            },
            "fission_type": {
                "type": "string",
                "description": f"(非必需) 裂变类型,   可供选择的数据:非裂变=0、修改=1、调整=2     例如: 0",
            },
            "front_low_efficiency": {
                "type": "string",
                "description": f"(非必需) 前测低效状态,   可供选择的数据:不是前侧低效=0、是前侧低效=1     例如: 0",
            }
        },
        "required": ["start_date", "end_date"],
    }

    async def execute(self, start_date: str, end_date: str, duration="", reject="", business_scene="", editor_uid="", photographer_uid="", director_uid="", brand_name="", product_name="", material_type="", autoadjust="", first_publish="", high_quality="", low_efficiency="", fission_type="", front_low_efficiency="") -> ToolResult:
        """
        执行JCMA API请求并返回原始数据。

        Args:
            start_date (str): 起始日期，格式为YYYY-MM-DD
            end_date (str): 结束日期，格式为YYYY-MM-DD
            duration (str): 可选[1-15, 16-30, 31-60, 61-120]
            reject (str): 可选项[-1, 0, 1]
            business_scene (str): 可选项[]
            editor_uid (str): 可选项[]
            photographer_uid (str):
        Returns:
            ToolResult: 包含API响应数据的工具结果
        """


        # 解析参数
        # 时长
        if duration != "":
            if not isinstance(duration, str):
                return ToolResult(error=f"请求JCMA API时发生错误: duration参数应该为string类型")
            if duration not in ['1-15', '16-30', '31-60', '60']:
                return ToolResult(error=f"请求JCMA API时发生错误: duration参数的可选项['1-15', '16-30', '31-60', '60']")
            duration_list = duration.split('-')
            new_duration_list = []
            for i in duration_list:
                new_duration_list.append(int(i))
        else:
            new_duration_list = []

        # 卡审状态
        reject_args = ''
        if reject != "":
            if not isinstance(reject, str):
                return ToolResult(error=f"请求JCMA API时发生错误: reject参数应该为string类型")
            if reject not in ['-1', '0', '1']:
                return ToolResult(error=f"请求JCMA API时发生错误: reject参数的可选项['-1', '0', '1']")
            if reject == '-1':
                reject_args = ''
            else:
                reject_args = reject

        # 业务场景
        if business_scene != "":
            try:
                business_scene = json.loads(business_scene)
            except:
                return ToolResult(error=f"请求JCMA API时发生错误: business_scene参数错误{business_scene}")
        else:
            business_scene = []
        # 剪辑人员
        if editor_uid != "":
            try:
                editor_uid = json.loads(editor_uid)
            except:
                return ToolResult(error=f"请求JCMA API时发生错误: editor_uid: {editor_uid}")

        # 拍摄人员
        if photographer_uid != "":
            try:
                photographer_uid = int(photographer_uid)
            except:
                return ToolResult(error=f"请求JCMA API时发生错误: photographer_uid: {photographer_uid}")

        # 编导人员
        if director_uid != "":
            try:
                director_uid = int(director_uid)
            except:
                return ToolResult(error=f"请求JCMA API时发生错误: director_uid: {director_uid}")

        if material_type != "":
            material_type = int(material_type)

        if autoadjust != "":
            autoadjust = int(autoadjust)

        if first_publish != "":
            first_publish = int(first_publish)

        if high_quality != "":
            high_quality = int(high_quality)

        if low_efficiency != "":
            low_efficiency = int(low_efficiency)

        if fission_type != "":
            try:
                fission_type = int(fission_type)
            except:
                return ToolResult(error=f"请求JCMA API时发生错误: fission_type: {fission_type}")

        if front_low_efficiency != "":
            front_low_efficiency = int(front_low_efficiency)

        try:

            data = await fetch_material_list(start_date=start_date, end_date=end_date, limit=20, duration=new_duration_list, reject=reject_args, business_scene=business_scene, editor_uid=editor_uid, photographer_uid=photographer_uid, director_uid=director_uid, brand_name=brand_name, product_name=product_name, material_type=material_type, autoadjust=autoadjust, first_publish=first_publish, high_quality=high_quality, low_efficiency=low_efficiency, fission_type=fission_type, front_low_efficiency=front_low_efficiency)
            os.makedirs("./tmp", exist_ok=True)
            # 将完整数据保存到文件（压缩版本，节省token）
            with open(os.path.abspath("./tmp/jcam_data.json"), "w", encoding="utf-8") as f:
                # json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                f.write(data)
                # json.dump(data, f, ensure_ascii=False)
            return ToolResult(
                output=f"数据获取成功，已保存到{os.path.abspath('./tmp/jcam_data.json')}文件中。共获取到{len(json.loads(data).get('data', {}).get('list', []))}条记录。"
            )

        except Exception as e:
            print(traceback.print_exc())
            return ToolResult(error=f"请求JCMA API时发生错误: {str(e)}")
