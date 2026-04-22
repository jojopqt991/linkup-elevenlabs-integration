                                                                                      


import os
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
LINKUP_API_KEY = os.environ["LINKUP_API_KEY"]
BASE = "https://api.elevenlabs.io/v1/convai"
HEADERS = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

tool_resp = requests.post(f"{BASE}/tools", headers=HEADERS, json={
    "tool_config": {
        "type": "webhook",
        "name": "linkup_web_search",
        "description": (
            "Search the web using Linkup. Use this when the user asks anything "
            "that needs current or factual information."
        ),
        "response_timeout_secs": 8,
        "api_schema": {
            "url": "https://api.linkup.so/v1/search",
            "method": "POST",
            "request_headers": {
                "Authorization": f"Bearer {LINKUP_API_KEY}",
                "Content-Type": "application/json",
            },
            "request_body_schema": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Natural language search query. Be specific.",
                    },
                    "depth": {"type": "string", "constant_value": "fast"},
                    "outputType": {"type": "string", "constant_value": "sourcedAnswer"},
                },
                "required": ["q"],
            },
        },
    }
})
tool_resp.raise_for_status()
tool_id = tool_resp.json()["id"]
print(f"Tool created: {tool_id}")
