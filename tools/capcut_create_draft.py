from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/create_draft"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        draft_id = tool_parameters["draft_id"]
        draft_width = tool_parameters["draft_width"]
        draft_height = tool_parameters["draft_height"]

        params = {
            "draft_id": draft_id,
            "draft_width":draft_width,
            "draft_height":draft_height,

        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
