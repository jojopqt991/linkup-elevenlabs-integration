# ElevenLabs x Linkup Integration

This guide walks through connecting Linkup to an ElevenLabs voice agent as a webhook tool.

This is useful anywhere an LLM's training cutoff or lack of citations breaks the experience: website live status, booking assistants that check today's availability, voice agents that brief users on current topics.

**Why Linkup fits voice specifically:**

- `sourcedAnswer` **returns a pre-synthesized, cited answer** -the LLM can read it near-verbatim instead of stitching snippets. Lower latency, lower hallucination risk.
- `depth: fast` **skips LLM processing** - raw results in ~1–2 seconds, inside the window voice conversations tolerate.
- **EU-based infrastructure** - worth noting if your agent operates in Europe.



Demo video: [https://youtu.be/Jijgka0nPKo](https://youtu.be/Jijgka0nPKo)

## How it works

1. User speaks to the voice agent
2. The LLM decides to call `linkup_web_search` for live information retrieval
3. ElevenLabs POSTs to `https://api.linkup.so/v1/search` with the headers and body you configured
4. The LLM-determined param (the search `q`) is merged with your fixed values (`depth`, `outputType`)
5. Linkup's results flow back to the LLM, which responds conversationally

## Prerequisites

Get your [Linkup API Key](https://app.linkup.so/home). 

Get your [ElevenLabs API Key](https://elevenlabs.io/app/developers/api-keys).

### Create tool and agent

Use the ElevenLabs [Create Tool API](https://elevenlabs.io/docs/api-reference/tools/create) to register a webhook tool that points to Linkup's search endpoint. Properties with `constant_value` are fixed on every request; properties with `description` are filled by the LLM at runtime.

```python
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
```

Save the returned `id` — you'll attach it to an agent next.

If you already have an agent, skip the next step and attach this tool from the ElevenLabs dashboard under **Agent > Tools**, or via the [Update Agent API](https://elevenlabs.io/docs/api-reference/agents/update). The tool won't do anything until it's attached.

Create a conversational agent and attach the webhook tool by its ID. Replace the tool id.

```python
import os
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
BASE = "https://api.elevenlabs.io/v1/convai"
HEADERS = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

tool_id = "[replace with tool id from previous step]"

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
```

Open the agent in the ElevenLabs dashboard to test it live:

```
https://elevenlabs.io/app/conversational-ai/agents/<YOUR_AGENT_ID>
```

Drop the agent into any webpage with two lines of HTML:

```html html theme={null}
<elevenlabs-convai agent-id="<YOUR_AGENT_ID>"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>
```

### Put It All Together

Full setup in one script: creates the webhook tool and a new agent with the tool attached in a single run.

```python

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

```

Run it:

```bash theme={null}
export ELEVENLABS_API_KEY="your-key"
export LINKUP_API_KEY="your-key"
python3 linkup_elevenlabs.py
```

## Choosing the right parameters

For most voice use cases, `depth: fast` + `outputType: sourcedAnswer` is the right default — it minimizes time-to-first-word and gives the LLM a cited answer it can read near-verbatim. Tune these based on what matters most for your agent.

### Search depth


| Depth      | Latency | Best for                                                                 |
| ---------- | ------- | ------------------------------------------------------------------------ |
| `fast`     | ~1–2s   | Voice assistants, real-time chat. No LLM processing — raw, fast results. |
| `standard` | ~5–10s  | Agents that need a balance of speed and reasoning over sources.          |
| `deep`     | ~20–30s | Research-oriented agents where a "let me think…" pause is acceptable.    |


Anything over ~3 seconds of silence tends to feel broken in a voice conversation, which is why `fast` is the default for voice agents.

### Output type


| Output type     | What it returns                            | Best for                                                          |
| --------------- | ------------------------------------------ | ----------------------------------------------------------------- |
| `sourcedAnswer` | Natural-language answer with cited sources | Voice agents — the LLM can read the answer near-verbatim.         |
| `searchResults` | List of result URLs + snippets             | Agents that want to synthesize the answer themselves.             |
| `structured`    | JSON matching a schema you define          | Task-specific agents (e.g., "find me a restaurant that serves…"). |


### Tuning by use case

- **Voice assistant / call agent** — `depth: fast`, `outputType: sourcedAnswer`. Optimize for time-to-first-word.
- **Voice research companion** — `depth: standard`, `outputType: sourcedAnswer`. Users will accept a short pause for richer answers.
- **Structured voice tasks** (booking, lookup) — `depth: standard`, `outputType: structured` with your own schema.

## Fixed vs. LLM-determined parameters

Each property in the `request_body_schema` is either fixed or dynamic:

- `**constant_value`** — sent on every request. The LLM never sees or modifies it. Use for `depth`, `outputType`, and any filters you want consistent across calls.
- `**description`** — the LLM fills the value at runtime based on this text. Use for `q` (the search query).

Keep as many parameters fixed as possible. Every LLM-determined parameter adds a reasoning step that increases response latency — something you really want to avoid in voice.

For the full ElevenLabs webhook tool schema, see the [ElevenLabs server tools documentation](https://elevenlabs.io/docs/conversational-ai/customization/tools/server-tools).

## Production notes

A few things worth getting right before shipping a voice agent to real users:

1. **Keep the webhook timeout short.** Voice is unforgiving of silence. `response_timeout_secs: 8` is a reasonable ceiling with `depth: fast` — if Linkup hasn't answered by then, it's better to degrade than to wait. Raise it only if you move to `standard` or `deep`.
2. **Prompt for graceful fallback.** Add a line to the agent prompt telling it what to say when search fails (the sample prompt above does this). Without it, the agent may go silent or hallucinate.
3. **Keep the tool description sharp.** The LLM decides whether to call Linkup based on the `description` field. A vague description leads to missed searches or over-triggering.
4. **Don't commit keys.** Use environment variables for `ELEVENLABS_API_KEY` and `LINKUP_API_KEY` — the consolidated script above already does.

## Next Steps

- Explore [Linkup's search API](https://docs.linkup.so) to customize your tool further
- Check out the [ElevenLabs Conversational AI docs](https://elevenlabs.io/docs/conversational-ai) to tune voice, model, and agent behavior

