from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_audio"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 定义处理空字符串的辅助函数
        def handle_empty_value(value):
            return None if value == '' else value

        # 解析参数（处理空字符串）
        audio_url = handle_empty_value(tool_parameters["audio_url"])  # 必需参数，确保不为空
        if audio_url is None:
            raise ValueError("audio_url is required and cannot be empty")

        # 处理数值类型参数（空字符串→None，否则转换为对应类型）
        start_str = handle_empty_value(tool_parameters["start"])
        start = float(start_str) if start_str is not None else 0.0

        end_str = handle_empty_value(tool_parameters["end"])
        end = float(end_str) if end_str is not None else None

        target_start_str = handle_empty_value(tool_parameters["target_start"])
        target_start = float(target_start_str) if target_start_str is not None else 0.0

        draft_id = handle_empty_value(tool_parameters["draft_id"])

        volume_str = handle_empty_value(tool_parameters["volume"])
        volume = float(volume_str) if volume_str is not None else 1.0

        track_name = handle_empty_value(tool_parameters["track_name"])
        if track_name is None:
            track_name = "audio_main"  # 默认轨道名称

        speed_str = handle_empty_value(tool_parameters["speed"])
        speed = float(speed_str) if speed_str is not None else 1.0

        sound_effects = handle_empty_value(tool_parameters["sound_effects"])
        params = {
            "audio_url": audio_url,
            "start":start,
            "end":end,
            "target_start":target_start,
            "draft_id":draft_id,
            "volume":volume,
            "track_name":track_name,
            "speed":speed,
            "sound_effects":sound_effects,
        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
