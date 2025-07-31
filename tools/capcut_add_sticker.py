from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_sticker"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        resource_id = tool_parameters.get("resource_id")
        draft_id = tool_parameters.get("draft_id")
        start = tool_parameters.get("start")
        end = tool_parameters.get("end")
        transform_x = float(tool_parameters.get("transform_x", 0.0))
        transform_y = float(tool_parameters.get("transform_y", 0.0))
        alpha = float(tool_parameters.get("alpha", 1.0))
        flip_horizontal = tool_parameters.get("flip_horizontal", False)
        flip_vertical = tool_parameters.get("flip_vertical", False)
        rotation = float(tool_parameters.get("rotation", 0.0))
        scale_x = float(tool_parameters.get("scale_x", 1.0))
        scale_y = float(tool_parameters.get("scale_y", 1.0))
        track_name = tool_parameters.get("track_name")
        relative_index = float(tool_parameters.get("relative_index", 0))
        width = float(tool_parameters.get("width", 1080))
        height = float(tool_parameters.get("height", 1920))

        # 构建参数字典（包含所有参数）
        params = {
            "resource_id": resource_id,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "alpha": alpha,
            "flip_horizontal": flip_horizontal,
            "flip_vertical": flip_vertical,
            "rotation": rotation,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "track_name": track_name,
            "relative_index": relative_index,
            "width": width,
            "height": height,
        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
