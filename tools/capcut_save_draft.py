from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

capcut_url = "http://192.168.110.26:9001/create_draft"

class CapcutTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        draft_id = tool_parameters.get("draft_id")
        draft_folder = tool_parameters.get("draft_folder")

        params = {
            "draft_id": draft_id,
            "draft_folder": draft_folder,
        }

        response = requests.post(capcut_url, json=params)
        response.raise_for_status()



        yield self.create_json_message({
            "response":response.json()
        })
