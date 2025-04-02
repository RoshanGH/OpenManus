import os
import aiohttp
import json
from typing import Dict, Any, Optional

from app.tool.base import BaseTool, ToolResult
from app.tool.v4_api import fetch_material_list

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
                "description": "(非必需) 视频时长区域，格式为1-15, 可选项[1-15, 16-30, 31-60, 60]",
            },
            "reject": {
                "type": "string",
                "description": "(非必需) 视频卡审状态，格式为-1=不做筛选, 0=未卡审, 1=卡审, 可选项[-1, 0, 1]",
            },
            "size": {
                "type": "string",
                "description": "(非必需) 视频卡审状态，格式为-1=不做筛选, 0=未卡审, 1=卡审, 可选项[-1, 0, 1]",
            }
        },
        "required": ["start_date", "end_date"],
    }

    async def execute(self, start_date: str, end_date: str, duration="", reject="") -> ToolResult:
        """
        执行JCMA API请求并返回原始数据。

        Args:
            start_date (str): 起始日期，格式为YYYY-MM-DD
            end_date (str): 结束日期，格式为YYYY-MM-DD
            duration (str): 可选[1-15, 16-30, 31-60, 61-120]
            reject (str): 可选项[-1, 0, 1]
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



        try:
            data = await fetch_material_list(start_date=start_date, end_date=end_date, limit=20, duration=new_duration_list, reject=reject_args)
            os.makedirs("./tmp", exist_ok=True)
            # 将完整数据保存到文件（压缩版本，节省token）
            with open(os.path.abspath("./tmp/jcam_data.json"), "w", encoding="utf-8") as f:
                # json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                f.write(data)
                # json.dump(data, f, ensure_ascii=False)
            return ToolResult(
                output=f"数据获取成功，已保存到{os.path.abspath('./tmp/jcam_data.json')}文件中。共获取到{len(data.get('data', {}).get('list', []))}条记录。"
            )

        except Exception as e:
            return ToolResult(error=f"请求JCMA API时发生错误: {str(e)}")
