from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/add_image"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        image_url = tool_parameters["image_url"]
        width = float(tool_parameters["width"])
        height = float(tool_parameters["height"])
        start = float(tool_parameters["start"]) if tool_parameters["start"] not in (None, "") else None
        end = float(tool_parameters["end"]) if tool_parameters["end"] not in (None, "") else None
        track_name = tool_parameters["track_name"]
        draft_id = tool_parameters["draft_id"]
        transform_x = float(tool_parameters["transform_x"]) if tool_parameters["transform_x"] not in (None, "") else None
        transform_y = float(tool_parameters["transform_y"]) if tool_parameters["transform_y"] not in (None, "") else None
        scale_x = float(tool_parameters["scale_x"]) if tool_parameters["scale_x"] not in (None, "") else None
        scale_y = float(tool_parameters["scale_y"]) if tool_parameters["scale_y"] not in (None, "") else None
        transition = tool_parameters["transition"]
        transition_duration = float(tool_parameters["transition_duration"]) if tool_parameters[
                                                                                   "transition_duration"] not in (None, "") else None

        # 新增：草稿文件夹路径
        draft_folder = tool_parameters["draft_folder"] if tool_parameters["draft_folder"] not in (None, "") else None

        # 新增：轨道渲染顺序
        try:
            relative_index = float(tool_parameters["relative_index"]) if tool_parameters["relative_index"] not in (None, "") else 0
        except Exception as e:
            relative_index = None
        # 新增：入场动画参数
        animation = tool_parameters["animation"]
        try:
            animation_duration = float(tool_parameters["animation_duration"]) if tool_parameters[
                                                                                 "animation_duration"] not in (None, "")  else 0.5
        except Exception as e:
            animation_duration = None
        # 新增：新入场动画参数（优先级更高）
        intro_animation = tool_parameters["intro_animation"]
        try:
            intro_animation_duration = float(tool_parameters["intro_animation_duration"]) if tool_parameters[
                                                                                             "intro_animation_duration"] not in (None, "") else 0.5
        except Exception as e:
            intro_animation_duration = 0.5
        # 新增：退场动画参数
        outro_animation = tool_parameters["outro_animation"]
        try:
            outro_animation_duration = float(tool_parameters["outro_animation_duration"]) if tool_parameters[
                                                                                             "outro_animation_duration"] not in (None, "") else 0.5
        except Exception as e:
            outro_animation_duration = 0.5
        # 新增：组合动画参数
        combo_animation = tool_parameters["combo_animation"]
        try:
            combo_animation_duration = float(tool_parameters["combo_animation_duration"]) if tool_parameters[
                                                                                             "combo_animation_duration"] not in (None, "") else 0.5
        except Exception as e:
            combo_animation_duration = 0.5
        mask_type = tool_parameters["mask_type"]
        mask_center_x = float(tool_parameters["mask_center_x"]) if tool_parameters["mask_center_x"] not in (None, "") else 0.0
        mask_center_y = float(tool_parameters["mask_center_y"]) if tool_parameters["mask_center_y"] not in (None, "") else 0.0
        mask_size = float(tool_parameters["mask_size"]) if tool_parameters["mask_size"] not in (None, "") else 0.5
        mask_rotation = float(tool_parameters["mask_rotation"]) if tool_parameters["mask_rotation"] not in (None, "") else 0.0
        mask_feather = float(tool_parameters["mask_feather"]) if tool_parameters["mask_feather"] not in (None, "") else 0.0
        mask_invert = tool_parameters["mask_invert"] == "True"  # 转换为布尔值
        mask_rect_width = float(tool_parameters["mask_rect_width"]) if tool_parameters[
                                                                           "mask_rect_width"] not in (None, "") else None
        mask_round_corner = float(tool_parameters["mask_round_corner"]) if tool_parameters[
                                                                               "mask_round_corner"] not in (None, "") else None

        # 构建完整参数
        params = {
            "image_url": image_url,
            "width": width,
            "height": height,
            "start": start,
            "end": end,
            "track_name": track_name,
            "draft_id": draft_id,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
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

            # 新增参数
            "draft_folder": draft_folder,
            "relative_index": relative_index,
            "animation": animation,
            "animation_duration": animation_duration,
            "intro_animation": intro_animation,
            "intro_animation_duration": intro_animation_duration,
            "outro_animation": outro_animation,
            "outro_animation_duration": outro_animation_duration,
            "combo_animation": combo_animation,
            "combo_animation_duration": combo_animation_duration
        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
