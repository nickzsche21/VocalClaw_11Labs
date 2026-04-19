# 🎙️ VocalClaw
### Multi-Agent Voice AI with Zero LLM Cost

> Built for the **ElevenLabs Agentic Summer Buildathon #1**

---

## What is VocalClaw?

VocalClaw fuses two open technologies into something new:

- **ElevenLabs** — handles ALL voice I/O (STT via Scribe + TTS via Conversational AI)
- **AirClaw** — handles ALL LLM inference, locally, for free

The result: a 4-agent voice AI system where every agent has a distinct voice, can hand off to each other, and costs **$0 in LLM fees** — forever.

---

## The Architecture

```
You speak
    │
    ▼
ElevenLabs Scribe (STT)
    │
    ▼
┌─────────────────────────────────────────────┐
│           ARIA — Orchestrator               │
│           Voice: Rachel (ElevenLabs)        │
│   Understands intent → routes to specialist │
└──────────┬──────────────────────────────────┘
           │
    ┌──────┼──────────┐
    ▼      ▼          ▼
  REX     LEX        MAX
 (Code) (Legal)  (Research)
 Domi   Bella    Antoni
  │      │          │
  └──────┴──────────┘
           │
           ▼
  ElevenLabs TTS
  (Agent's unique voice)
           │
           ▼
      You hear it
```

**Every handoff is spoken aloud.** Aria announces routing. Each specialist responds in their own distinct ElevenLabs voice.

---

## Agents

| Agent | Role | ElevenLabs Voice | Handles |
|-------|------|-----------------|---------|
| **Aria** | Orchestrator | Rachel | Intent detection, routing, fallback answers |
| **Rex** | Code Specialist | Domi | Programming, debugging, architecture |
| **Lex** | Legal Specialist | Bella | Legal research, case analysis, statutes |
| **Max** | Research Specialist | Antoni | General research, facts, summaries |

---

## Why This Wins

Most "agentic voice AI" demos use OpenAI for inference — $0.01–0.06 per 1K tokens, forever. VocalClaw runs AirClaw locally: **inference is free, unlimited, and private.**

ElevenLabs does what it does best — the most natural, expressive TTS in the world. AirClaw does what it does best — local, OpenAI-compatible inference at zero marginal cost.

This is the architecture that makes voice AI economically viable at scale.

---

## Tech Stack

- **Voice Input**: ElevenLabs Scribe (STT)
- **Voice Output**: ElevenLabs TTS (4 distinct voices)
- **LLM Inference**: AirClaw (local, OpenAI-compatible)
- **Orchestration**: Python multi-agent system with intent classification
- **Frontend**: HTML/JS, WebSocket mic capture
- **Backend**: FastAPI

---

## Setup & Run

### 1. Install AirClaw
```bash
pip install airclaw
airclaw start
# Runs OpenAI-compatible API at localhost:1234
```

### 2. Clone & Configure
```bash
git clone https://github.com/nickzsche21/AirClaw-VocalClaw_11Labs
cd AirClaw-VocalClaw_11Labs
pip install -r requirements.txt
```

### 3. Set API Key
```bash
export ELEVENLABS_API_KEY="your_key_here"
```

### 4. Run
```bash
bash run.sh
# Open localhost:8080
# Hold mic button → talk → hear agents respond
```

---

## Demo Flow

1. Ask: *"Can you explain the difference between IPC Section 302 and 304?"*
2. Aria detects legal intent → announces handoff to Lex
3. **Lex responds in Bella's voice** with a structured legal breakdown
4. Ask: *"Write me a Python function to parse that statute text"*
5. Aria detects code intent → announces handoff to Rex
6. **Rex responds in Domi's voice** with working code

Two questions. Two different voices. One seamless system.

---

## Built By

**Nick** — Founder, JurixAI (AI legal research for the Indian market)

> JurixAI is backed by NSRCEL IIM Bangalore, IIM Lucknow EIC, AIC-BHU, and the Perplexity AI Fellowship. VocalClaw's Lex agent is a direct prototype of what localized legal AI agents sound like in production.

---

## License

MIT — build on it.
