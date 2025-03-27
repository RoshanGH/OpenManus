import os
import aiohttp
import json
from typing import Dict, Any, Optional

from app.tool.base import BaseTool, ToolResult


class JcamApiTool(BaseTool):
    name: str = "jcam_api"
    description: str = """
    请求JCAM公司API并获取指定日期范围内的数据。
    该工具用于获取JCAM公司的视频素材信息，包括编导、摄影师、剪辑师等相关数据。
    当用户询问关于JCAM公司数据、编导数据统计、素材分析等问题时，应使用此工具获取原始数据。
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
        },
        "required": ["start_date", "end_date"],
    }

    async def execute(self, start_date: str, end_date: str) -> ToolResult:
        """
        执行JCAM API请求并返回原始数据。

        Args:
            start_date (str): 起始日期，格式为YYYY-MM-DD
            end_date (str): 结束日期，格式为YYYY-MM-DD

        Returns:
            ToolResult: 包含API响应数据的工具结果
        """
        try:
            # 构建请求参数
            date_param = [start_date, end_date]

            # 发送API请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api.php",
                    json={"date": date_param}
                ) as response:
                    if response.status != 200:
                        return ToolResult(
                            error=f"API请求失败，状态码: {response.status}"
                        )

                    # 解析响应数据
                    data = await response.json()

                    # 检查响应状态
                    if data.get("status") != "success":
                        return ToolResult(
                            error=f"API返回错误: {data.get('message', '未知错误')}"
                        )

                    # # 返回原始数据，让大模型进行分析
                    # return ToolResult(
                    #     output=json.dumps(data, ensure_ascii=False, indent=2)
                    # )

                    # 确保tmp目录存在
                    os.makedirs("./tmp", exist_ok=True)

                    # 将完整数据保存到文件（压缩版本，节省token）
                    with open(os.path.abspath("./tmp/jcam_data.json"), "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

                    # 返回简短的成功消息，而不是完整数据
                    return ToolResult(
                        output=f"数据获取成功，已保存到{os.path.abspath("./tmp/jcam_data.json")}文件中。共获取到{len(data.get('data', {}).get('list', []))}条记录。"
                    )
        except Exception as e:
            return ToolResult(error=f"请求JCAM API时发生错误: {str(e)}")
