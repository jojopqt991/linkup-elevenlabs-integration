import os
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
LINKUP_API_KEY = os.environ["LINKUP_API_KEY"]
BASE = "https://api.elevenlabs.io/v1/convai"
HEADERS = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

# 1. Create webhook tool
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

# 2. Create agent with the tool attached
agent_resp = requests.post(f"{BASE}/agents/create", headers=HEADERS, json={
    "name": "Linkup Search Assistant",
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": (
                    "You are a helpful voice assistant with real-time web search "
                    "powered by Linkup. When users ask questions that need current "
                    "information, use the linkup_web_search tool.\n\n"
                    "Guidelines:\n"
                    "- Search proactively for time-sensitive or factual questions.\n"
                    "- Summarize results conversationally — do not read URLs aloud.\n"
                    "- Cite sources naturally.\n"
                    "- Keep responses concise — this is voice.\n"
                    "- If the search tool fails or times out, tell the user you "
                    "couldn't find that information right now and offer to try again."
                ),
                "tool_ids": [tool_id],
            },
            "first_message": "Hey! I can search the web for you. What would you like to know?",
        }
    },
})
agent_resp.raise_for_status()
agent_id = agent_resp.json()["agent_id"]
print(f"Agent created: {agent_id}")
print(f"Dashboard: https://elevenlabs.io/app/conversational-ai/agents/{agent_id}")
