# ⚡ VocalClaw

### Multi-Agent Voice AI — ElevenLabs voices × AirClaw local LLM

> Talk to four specialized AI agents, each with a distinct voice.  
> ElevenLabs handles all voice I/O. AirClaw handles all LLM inference — locally, at **$0/month**.

Built for the **ElevenLabs Agentic Summer Buildathon**.

---

## What it does

VocalClaw is a multi-agent voice AI system where:

- 🎤 **You speak** → ElevenLabs STT transcribes your voice
- 🧠 **AirClaw** routes your query to the right local LLM (Mistral, Llama, DeepSeek — your machine)
- 🔀 **Agent orchestration** — Aria (the lead agent) decides whether to answer or hand off to a specialist
- 🔊 **ElevenLabs TTS** synthesizes the response in each agent's distinct voice
- 💬 **You hear** — a professional-grade AI response, spoken back to you in real-time

---

## The Agents

| Agent | Voice | Specialty |
|-------|-------|-----------|
| **Aria** ✦ | Rachel (ElevenLabs) | Orchestrator, general assistant |
| **Rex** ⚡ | Domi (ElevenLabs) | Code & technical questions |
| **Lex** ⚖ | Bella (ElevenLabs) | Legal intelligence, contracts |
| **Max** ◎ | Antoni (ElevenLabs) | Research & information |

Aria automatically routes your query to the right specialist. Each handoff is spoken aloud with a natural transition.

---

## Architecture

```
Your Voice
    │
    ▼
ElevenLabs STT (Scribe v1)
    │
    ▼
VocalClaw Server (FastAPI + WebSocket)
    │
    ├──── Agent Orchestrator (Aria)
    │         │
    │         ├── Route to Rex? ──┐
    │         ├── Route to Lex? ──┤
    │         └── Route to Max? ──┤
    │                             │
    ▼                             ▼
AirClaw (localhost:4096)   ←── All LLM calls
[Mistral / Llama / DeepSeek / any HuggingFace model]
    │
    ▼
ElevenLabs TTS (Turbo v2.5)
    │
    ▼
Voice Response (MP3 stream → browser)
```

**The key insight:** ElevenLabs handles what it does best — voice quality, STT accuracy, low-latency TTS. AirClaw handles what it does best — running 7B–70B models locally, for free, with full privacy.

---

## Why this matters

| | Traditional Voice AI | VocalClaw |
|---|---|---|
| LLM cost | $50–$150/month | **$0** |
| Data privacy | Cloud LLM sees everything | **100% local inference** |
| Voice quality | Robotic TTS | **ElevenLabs — human-grade** |
| Multi-agent | Single monolithic bot | **4 specialized agents, auto-routing** |
| Setup | Complex | **1 command** |

---

## Quick Start

### Prerequisites
- Python 3.10+
- [AirClaw](https://github.com/nickzsche21/airclaw) (for local LLM)
- ElevenLabs API key

### Run

```bash
# Terminal 1 — start local LLM
pip install airclaw
airclaw start

# Terminal 2 — start VocalClaw
git clone https://github.com/your-repo/vocalclaw
cd vocalclaw

export ELEVENLABS_API_KEY="your_key_here"
bash run.sh
```

Open `http://localhost:8080`, hold the mic button, and talk.

### Custom LLM endpoint

AirClaw exposes any local model as an OpenAI-compatible API. Point VocalClaw to it:

```bash
AIRCLAW_URL=http://localhost:4096/v1 bash run.sh
```

Works with any OpenAI-compatible server: Ollama, LM Studio, llama.cpp, vLLM.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Voice Input | ElevenLabs Scribe STT |
| Voice Output | ElevenLabs Turbo TTS v2.5 |
| Agent System | Custom Python (FastAPI + WebSocket) |
| LLM Backend | AirClaw → local model via RabbitLLM/AirLLM |
| Frontend | Vanilla JS + Web Audio API |
| Server | FastAPI (async) |

---

## About AirClaw

[AirClaw](https://github.com/nickzsche21/airclaw) is an open-source Python package that runs 70B parameter models on a 4GB GPU and exposes them as an OpenAI-compatible API server. It uses RabbitLLM (preferred) or AirLLM as backends, enabling layer-by-layer inference for low-VRAM systems.

```bash
pip install airclaw
airclaw start  # starts Mistral 7B by default
# → OpenAI-compatible server at localhost:4096
```

---

## Built by

[Nikhil Kumar](https://github.com/nickzsche21) — Founder, JurixAI  
ElevenLabs Agentic Summer Buildathon 2025

---

## License

MIT
