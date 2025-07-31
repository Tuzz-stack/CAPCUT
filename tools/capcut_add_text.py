from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_text"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        text = tool_parameters["input_text"]

        # 必传参数，不允许为空
        start_val = tool_parameters["start"]
        start = float(start_val) if start_val not in (None, '') else 0.0

        end_val = tool_parameters["end"]
        end = float(end_val) if end_val not in (None, '') else 0.0

        font = tool_parameters["font"]
        font_color = tool_parameters["font_color"]

        font_size_val = tool_parameters["font_size"]
        font_size = round(float(font_size_val)) if font_size_val not in (None, '') else 24

        # 位置参数
        transform_y_val = tool_parameters.get("transform_y", -0.8)
        transform_y = float(transform_y_val) if transform_y_val not in (None, '') else -0.8

        transform_x_val = tool_parameters.get("transform_x", 0)
        transform_x = float(transform_x_val) if transform_x_val not in (None, '') else 0

        vertical = tool_parameters.get("vertical", "False").lower() == "true"

        # 样式参数
        font_alpha_val = tool_parameters.get("font_alpha", 1.0)
        font_alpha = float(font_alpha_val) if font_alpha_val not in (None, '') else 1.0

        border_alpha_val = tool_parameters.get("border_alpha", 1.0)
        border_alpha = float(border_alpha_val) if border_alpha_val not in (None, '') else 1.0

        border_color = tool_parameters.get("border_color", "#000000")

        border_width_val = tool_parameters.get("border_width", 0.0)
        border_width = float(border_width_val) if border_width_val not in (None, '') else 0.0

        background_color = tool_parameters.get("background_color", "#000000")

        background_style_val = tool_parameters.get("background_style", 1)
        background_style = float(background_style_val) if background_style_val not in (None, '') else 1.0

        background_alpha_val = tool_parameters.get("background_alpha", 0.0)
        background_alpha = float(background_alpha_val) if background_alpha_val not in (None, '') else 0.0

        # 特效参数
        bubble_effect_id = tool_parameters.get("bubble_effect_id")
        bubble_resource_id = tool_parameters.get("bubble_resource_id")
        effect_effect_id = tool_parameters.get("effect_effect_id")

        # 动画参数
        intro_animation = tool_parameters.get("intro_animation", "none")

        intro_duration_val = tool_parameters.get("intro_duration", 0.5)
        intro_duration = float(intro_duration_val) if intro_duration_val not in (None, '') else 0.5

        outro_animation = tool_parameters.get("outro_animation", "none")

        outro_duration_val = tool_parameters.get("outro_duration", 0.5)
        outro_duration = float(outro_duration_val) if outro_duration_val not in (None, '') else 0.5

        # 视频尺寸参数
        width_val = tool_parameters.get("width", 1920)
        width = float(width_val) if width_val not in (None, '') else 1920.0

        height_val = tool_parameters.get("height", 1080)
        height = float(height_val) if height_val not in (None, '') else 1080.0

        fixed_width_val = tool_parameters.get("fixed_width", -1)
        fixed_width = float(fixed_width_val) if fixed_width_val not in (None, '') else -1.0

        fixed_height_val = tool_parameters.get("fixed_height", -1)
        fixed_height = float(fixed_height_val) if fixed_height_val not in (None, '') else -1.0

        # 构建平面参数结构
        params = {
            "text": text,
            "start": start,
            "end": end,
            "font": font,
            "font_color": font_color,
            "font_size": font_size,
            "transform_y": transform_y,
            "transform_x": transform_x,
            "vertical": vertical,
            "font_alpha": font_alpha,
            "border_alpha": border_alpha,
            "border_color": border_color,
            "border_width": border_width,
            "background_color": background_color,
            "background_style": background_style,
            "background_alpha": background_alpha,
            "bubble_effect_id": bubble_effect_id,
            "bubble_resource_id": bubble_resource_id,
            "effect_effect_id": effect_effect_id,
            "intro_animation": intro_animation,
            "intro_duration": intro_duration,
            "outro_animation": outro_animation,
            "outro_duration": outro_duration,
            "width": width,
            "height": height,
            "fixed_width": fixed_width,
            "fixed_height": fixed_height
        }

        # 移除值为None的键
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
