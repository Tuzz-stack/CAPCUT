from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_video"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 从工具参数中解析所有视频轨道参数
        # 定义处理空字符串的辅助函数
        def handle_empty_value(value):
            return None if value == '' else value

        # 解析参数（处理空字符串）
        draft_folder = handle_empty_value(tool_parameters.get("draft_folder"))
        video_url = tool_parameters["video_url"]  # 必需参数（确保不为空）

        # 处理宽度（空字符串→None，否则用默认值1080）
        width_str = handle_empty_value(tool_parameters.get("width"))
        width = int(width_str) if width_str is not None else 1080

        # 处理高度（空字符串→None，否则用默认值1920）
        height_str = handle_empty_value(tool_parameters.get("height"))
        height = int(height_str) if height_str is not None else 1920

        # 处理起始时间（空字符串→None，否则用默认值0）
        start_str = handle_empty_value(tool_parameters.get("start"))
        start = float(start_str) if start_str is not None else 0

        # 处理结束时间（空字符串→None，无参数→None）
        end_str = handle_empty_value(tool_parameters.get("end"))
        end = float(end_str) if end_str is not None else None

        # 处理目标起始时间（空字符串→None，否则用默认值0）
        target_start_str = handle_empty_value(tool_parameters.get("target_start"))
        target_start = float(target_start_str) if target_start_str is not None else 0

        draft_id = handle_empty_value(tool_parameters.get("draft_id"))

        # 处理Y轴位移（空字符串→None，否则用默认值0）
        transform_y_str = handle_empty_value(tool_parameters.get("transform_y"))
        transform_y = float(transform_y_str) if transform_y_str is not None else 0

        # 处理X轴缩放（空字符串→None，否则用默认值1）
        scale_x_str = handle_empty_value(tool_parameters.get("scale_x"))
        scale_x = float(scale_x_str) if scale_x_str is not None else 1

        # 处理Y轴缩放（空字符串→None，否则用默认值1）
        scale_y_str = handle_empty_value(tool_parameters.get("scale_y"))
        scale_y = float(scale_y_str) if scale_y_str is not None else 1

        # 处理X轴位移（空字符串→None，否则用默认值0）
        transform_x_str = handle_empty_value(tool_parameters.get("transform_x"))
        transform_x = float(transform_x_str) if transform_x_str is not None else 0

        # 处理播放速度（空字符串→None，否则用默认值1.0）
        speed_str = handle_empty_value(tool_parameters.get("speed"))
        speed = float(speed_str) if speed_str is not None else 1.0

        track_name = handle_empty_value(tool_parameters.get("track_name"))

        # 处理相对索引（空字符串→None，否则用默认值0）
        relative_index_str = handle_empty_value(tool_parameters.get("relative_index"))
        relative_index = int(relative_index_str) if relative_index_str is not None else 0

        # 处理时长（空字符串→None，无参数→None）
        duration_str = handle_empty_value(tool_parameters.get("duration"))
        duration = float(duration_str) if duration_str is not None else None

        transition = handle_empty_value(tool_parameters.get("transition"))

        # 处理转场时长（空字符串→None，无参数→None）
        transition_duration_str = handle_empty_value(tool_parameters.get("transition_duration"))
        transition_duration = float(transition_duration_str) if transition_duration_str is not None else None

        mask_type = handle_empty_value(tool_parameters.get("mask_type"))

        # 处理蒙版X轴中心（空字符串→None，否则用默认值0.5）
        mask_center_x_str = handle_empty_value(tool_parameters.get("mask_center_x"))
        mask_center_x = float(mask_center_x_str) if mask_center_x_str is not None else 0.5

        # 处理蒙版Y轴中心（空字符串→None，否则用默认值0.5）
        mask_center_y_str = handle_empty_value(tool_parameters.get("mask_center_y"))
        mask_center_y = float(mask_center_y_str) if mask_center_y_str is not None else 0.5

        # 处理蒙版大小（空字符串→None，否则用默认值1.0）
        mask_size_str = handle_empty_value(tool_parameters.get("mask_size"))
        mask_size = float(mask_size_str) if mask_size_str is not None else 1.0

        # 处理蒙版旋转角度（空字符串→None，否则用默认值0.0）
        mask_rotation_str = handle_empty_value(tool_parameters.get("mask_rotation"))
        mask_rotation = float(mask_rotation_str) if mask_rotation_str is not None else 0.0

        # 处理蒙版羽化（空字符串→None，否则用默认值0.0）
        mask_feather_str = handle_empty_value(tool_parameters.get("mask_feather"))
        mask_feather = float(mask_feather_str) if mask_feather_str is not None else 0.0

        # 处理蒙版反转（空字符串→None，否则用默认值False）
        mask_invert_str = handle_empty_value(tool_parameters.get("mask_invert"))
        mask_invert = mask_invert_str.lower() == "true" if mask_invert_str is not None else False

        # 处理矩形蒙版宽度（空字符串→None，无参数→None）
        mask_rect_width_str = handle_empty_value(tool_parameters.get("mask_rect_width"))
        mask_rect_width = float(mask_rect_width_str) if mask_rect_width_str is not None else None

        # 处理矩形蒙版圆角（空字符串→None，无参数→None）
        mask_round_corner_str = handle_empty_value(tool_parameters.get("mask_round_corner"))
        mask_round_corner = int(mask_round_corner_str) if mask_round_corner_str is not None else None

        # 处理音量（空字符串→None，否则用默认值1.0）
        volume_str = handle_empty_value(tool_parameters.get("volume"))
        volume = float(volume_str) if volume_str is not None else 1.0

        # 构建完整的参数对象
        params = {
            "draft_folder": draft_folder,
            "video_url": video_url,
            "width": width,
            "height": height,
            "start": start,
            "end": end,
            "target_start": target_start,
            "draft_id": draft_id,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "transform_x": transform_x,
            "speed": speed,
            "track_name": track_name,
            "relative_index": relative_index,
            "duration": duration,
            "transition": transition,
            "transition_duration": transition_duration,
            "mask_type": mask_type,
            "mask_center_x": mask_center_x,
            "mask_center_y": mask_center_y,
            "mask_size": mask_size,
            "mask_rotation": mask_rotation,
            "mask_feather": mask_feather,
            "mask_invert": mask_invert,
            "mask_rect_width": mask_rect_width,
            "mask_round_corner": mask_round_corner,
            "volume": volume
        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
