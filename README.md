<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0d1117,100:161b22&height=180&section=header&text=AI%20Pizza%20Ordering%20Agent&fontSize=40&fontColor=e6edf3&fontAlignY=42&desc=Voice%20ordering%20agent%20on%20LiveKit%20and%20OpenAI%20Realtime&descSize=15&descColor=8b949e&descAlignY=64" width="100%"/>

**A compact voice agent that takes pizza orders by phone-style conversation, using tool calls against a mock menu and order backend.**

![Python](https://img.shields.io/badge/Python-161b22?style=for-the-badge&logo=python&logoColor=58a6ff)
![LiveKit](https://img.shields.io/badge/LiveKit_Agents-161b22?style=for-the-badge&logo=livekit&logoColor=58a6ff)
![OpenAI](https://img.shields.io/badge/OpenAI_Realtime-161b22?style=for-the-badge&logo=openai&logoColor=58a6ff)

</div>

## Overview

A small, focused demo of a speech-to-speech ordering agent. A LiveKit Agents worker joins a room, hands the caller's audio to an OpenAI Realtime model, and lets the model call four Python tools to read the menu and create or look up orders. The pizzeria, menu and orders are fictional and live in memory. The agent persona speaks Ukrainian.

## Highlights

- Speech-to-speech through a single `gpt-realtime-mini` session: no separate STT, LLM or TTS stages are wired in the code.
- Four function tools exposed to the model: `get_menu`, `get_item_details`, `create_order`, `get_order_status`.
- Tools are validated against data: unknown or unavailable items are rejected by `create_order`, and the total is computed server-side from menu prices.
- Tolerant tool inputs: order IDs such as `101`, `ORD101` and `ORD-101` are normalized, status can be looked up by customer name, and Ukrainian category names map to canonical ones.
- A detailed system prompt (about 70 lines) constrains scope, price disclosure, availability wording and voice-friendly style, and refuses prompt-extraction requests.

## How it works

```mermaid
sequenceDiagram
    participant C as Caller
    participant L as LiveKit room
    participant A as Agent worker (agent.py)
    participant R as OpenAI Realtime
    participant T as Tools (src/agent/tools.py)
    participant O as In-memory menu and orders

    C->>L: Audio track
    L->>A: Job dispatched, entrypoint connects (audio only)
    A->>R: Stream audio, system prompt, tool schemas
    R-->>A: Spoken reply (audio)
    A-->>L: Agent audio
    L-->>C: Playback
    R->>A: Function call (e.g. get_menu)
    A->>T: Execute tool
    T->>O: Read menu or order state
    O-->>T: JSON result
    T-->>R: Tool output
    R->>A: create_order(items, name, phone, address)
    A->>T: Execute tool
    T->>O: Validate items, store order, return ID and total
    R-->>C: Spoken confirmation (via LiveKit)
```

## Tech stack

| Layer | Choice |
| --- | --- |
| Language | Python |
| Realtime transport and worker | LiveKit Agents (`livekit-agents`, `AgentSession`, `cli.run_app`) |
| Voice model | OpenAI Realtime via `livekit-plugins-openai` (`gpt-realtime-mini`) |
| Tools | `llm.function_tool` with typed, annotated parameters |
| Data | Python dicts in `src/api/fake_api.py` (no database) |
| Config | `python-dotenv` |

## Quick start

Python version is not pinned in the repo; use a version supported by current `livekit-agents`. You need a LiveKit server (Cloud or self-hosted) and an OpenAI API key.

```bash
pip install -r requirements.txt
# create .env with the variables listed below
python agent.py dev
```

`dev` starts the worker in LiveKit's development mode. Connect to the room with any LiveKit client (for example the LiveKit Agents Playground) to talk to the agent.

## Configuration

Set in `.env` (git-ignored; loaded by `python-dotenv`). These are the standard variables read by the LiveKit CLI and the OpenAI plugin; `agent.py` itself does not read them directly.

| Variable | Purpose |
| --- | --- |
| `LIVEKIT_URL` | LiveKit server WebSocket URL (`wss://...`) |
| `LIVEKIT_API_KEY` | LiveKit API key |
| `LIVEKIT_API_SECRET` | LiveKit API secret |
| `OPENAI_API_KEY` | OpenAI key for the Realtime model |

## Project structure

```text
agent.py              Worker entrypoint: Agent, RealtimeModel, AgentSession
requirements.txt      livekit-agents, livekit-plugins-openai, python-dotenv
src/agent/prompts.py  System prompt (Ukrainian, pizzeria persona and rules)
src/agent/tools.py    Four function tools wrapping the mock API
src/api/fake_api.py   In-memory menu (10 items), seeded orders, order logic
```

## Status and roadmap

Working demo, not a product. Known limits:

- Orders and the ID counter live in process memory and are lost on restart; the "API" is a mock.
- `create_order` requires an address, so pickup orders are not modelled even though the prompt mentions pickup.
- Voice activity detection, turn handling and interruption settings use library defaults and are not tuned.
- No tests, no latency measurements, no LICENSE file, no deployment config.

Possible next steps: a real order backend, a pickup flow, tests for the tools, and measured latency.
