from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_subtitle"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        srt_path = tool_parameters["srt_path"]

        # 可选字符串参数
        draft_id = tool_parameters.get("draft_id")
        track_name = tool_parameters.get("track_name", "subtitle")
        font = tool_parameters.get("font")
        font_color = tool_parameters.get("font_color", "#FFFFFF")
        border_color = tool_parameters.get("border_color", "#000000")
        background_color = tool_parameters.get("background_color", "#000000")
        bubble_effect_id = tool_parameters.get("bubble_effect_id")
        bubble_resource_id = tool_parameters.get("bubble_resource_id")
        effect_effect_id = tool_parameters.get("effect_effect_id")
        style_reference = tool_parameters.get("style_reference")

        # 数值参数并使用float转换
        time_offset = float(tool_parameters.get("time_offset", 0.0))
        font_size = float(tool_parameters.get("font_size", 8.0))
        border_alpha = float(tool_parameters.get("border_alpha", 1.0))
        border_width = float(tool_parameters.get("border_width", 0.0))
        background_alpha = float(tool_parameters.get("background_alpha", 0.0))
        transform_x = float(tool_parameters.get("transform_x", 0.0))
        transform_y = float(tool_parameters.get("transform_y", -0.8))
        scale_x = float(tool_parameters.get("scale_x", 1.0))
        scale_y = float(tool_parameters.get("scale_y", 1.0))
        rotation = float(tool_parameters.get("rotation", 0.0))
        alpha = float(tool_parameters.get("alpha", 0.4))

        # 整数参数
        background_style = int(tool_parameters.get("background_style", 1))
        width = int(tool_parameters.get("width", 1080))
        height = int(tool_parameters.get("height", 1920))

        # 布尔参数
        bold = bool(tool_parameters.get("bold", False))
        italic = bool(tool_parameters.get("italic", False))
        underline = bool(tool_parameters.get("underline", False))
        vertical = bool(tool_parameters.get("vertical", True))

        # 构建参数字典
        params = {
            "srt": srt_path,
            "draft_id": draft_id,
            "track_name": track_name,
            "time_offset": time_offset,
            "font": font,
            "font_size": font_size,
            "bold": bold,
            "italic": italic,
            "underline": underline,
            "font_color": font_color,
            "border_alpha": border_alpha,
            "border_color": border_color,
            "border_width": border_width,
            "background_color": background_color,
            "background_style": background_style,
            "background_alpha": background_alpha,
            "bubble_effect_id": bubble_effect_id,
            "bubble_resource_id": bubble_resource_id,
            "effect_effect_id": effect_effect_id,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "rotation": rotation,
            "style_reference": style_reference,
            "vertical": vertical,
            "alpha": alpha,
            "width": width,
            "height": height
        }
        response = requests.post(capcut_url, json=params)
        response.raise_for_status()


        yield self.create_json_message({
            "response":response.json()
        })
