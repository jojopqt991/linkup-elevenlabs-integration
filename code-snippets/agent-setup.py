import os
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
BASE = "https://api.elevenlabs.io/v1/convai"
HEADERS = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

tool_id = "tool_2601kptc7threep8fk9jdw0s0nw5"

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
