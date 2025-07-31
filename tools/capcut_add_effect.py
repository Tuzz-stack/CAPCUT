from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_effect"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 从工具参数中提取所有参数
        effect_type = tool_parameters.get("effect_type")
        start = int(tool_parameters.get("start", 0))
        end = int(tool_parameters.get("end", 3))
        draft_id = tool_parameters.get("draft_id")
        track_name = tool_parameters.get("track_name")
        params_list = tool_parameters.get("params")

        # 处理空列表或 None 的情况
        if params_list in (None, [], "[]"):
            params_list = None
        else:
            # 处理字符串形式的列表
            if isinstance(params_list, str):
                elements = params_list.strip('[]').split(',')
                try:
                    params_list = [int(e.strip()) for e in elements if e.strip()]
                except ValueError:
                    params_list = None
            # 处理已经是列表的情况
            elif isinstance(params_list, list):
                try:
                    params_list = [int(e) for e in params_list]
                except (ValueError, TypeError):
                    params_list = None
            # 其他情况
            else:
                params_list = None
        width = int(tool_parameters.get("width", 1080))
        height = int(tool_parameters.get("height", 1920))

        # 构建完整的参数字典
        params = {
            "effect_type": effect_type,
            "start": start,
            "end": end,
            "draft_id": draft_id,
            "track_name": track_name,
            "params": params_list,
            "width": width,
            "height": height
        }

        # 验证必填参数
        if not effect_type:
            raise ValueError("effect_type是必填参数")

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
