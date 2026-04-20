# 🎙️ VocalClaw
### Multi-Agent Voice AI — Built for ElevenLabs Agentic Summer Buildathon

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-7C3AED?style=flat-square)](https://vocalclaw11labs-6sqxrv2exz5ce62sn3n7cy.streamlit.app)

---

## What is VocalClaw?

VocalClaw is a multi-agent voice AI system where **four specialized AI agents — each with a distinct ElevenLabs voice — collaborate to answer your questions.**

You speak. Agents think. You hear the answer — automatically, in the right expert's voice.

**The philosophy:** LLM inference should cost $0. ElevenLabs should handle everything voice-related. That's the stack.

- **ElevenLabs** — Voice I/O (Scribe STT + TTS for all 4 agents)
- **Groq** — Free-tier LLM inference (inspired by AirClaw's zero-cost local inference philosophy)
- **No OpenAI. No per-token costs. No paywalls.**

> *VocalClaw is architecturally inspired by [AirClaw](https://github.com/nickzsche21/AirClaw) — the belief that AI inference should be free and open. AirClaw runs locally; VocalClaw extends that philosophy to the cloud using Groq's free API.*

---

## 🎯 Two Modes

### Solo Mode
You ask → Aria detects intent → routes to the right specialist → **that agent responds in their unique voice**

Aria even *speaks the handoff* before passing to the specialist. That's agentic behaviour.

### ⚡ Council Mode — The Killer Feature
You ask ONE question → **all 4 agents respond in sequence, each in their own voice** → Aria synthesizes a final answer

You literally hear a 4-voice AI debate. No other voice AI does this.

---

## The Agents

| Agent | Voice | Speciality |
|-------|-------|-----------|
| 🎯 **Aria** | Rachel | Orchestrator — routes, synthesizes, opens council |
| 💻 **Rex** | Domi | Code — programming, debugging, architecture |
| ⚖️ **Lex** | Bella | Legal — Indian law, IPC, CrPC, case precedents |
| 🔬 **Max** | Antoni | Research — science, history, economics, facts |

---

## Architecture

```
🎤 You speak
     │
     ▼
ElevenLabs Scribe STT
     │
     ▼
┌─────────────────────────┐
│  ARIA — Orchestrator    │
│  Intent detection       │
│  Routes + announces     │
└──────┬──────────────────┘
       │ speaks handoff aloud
  ┌────┼────────┐
  ▼    ▼        ▼
 REX  LEX      MAX
(Code)(Legal)(Research)
       │
       ▼
ElevenLabs TTS — Agent's unique voice
       │
       ▼
🔊 Autoplays instantly
```

---

## Features

- 🎤 **Mic input** — record your question directly in browser
- 🔊 **ElevenLabs Scribe STT** — transcribes your voice instantly
- 🤖 **Real AI via Groq** (LLaMA 3) — not templates
- 🗣️ **Aria speaks handoffs** — announces routing in her own voice
- ⚡ **Council Mode** — 4 agents, 4 voices, 1 question, 1 synthesized answer
- 🔁 **Autoplay** — audio fires automatically, no click needed
- 💬 **Session history** — full conversation thread

---

## Live Demo

👉 **[vocalclaw11labs-6sqxrv2exz5ce62sn3n7cy.streamlit.app](https://vocalclaw11labs-6sqxrv2exz5ce62sn3n7cy.streamlit.app)**

Try these:
- *"Explain IPC Section 302"* → Lex responds in Bella's voice
- *"Write a Python web scraper"* → Rex responds in Domi's voice
- **Council Mode** + *"Should I raise a seed round or bootstrap?"* → hear all 4 voices debate it

---

## Run Locally

```bash
git clone https://github.com/nickzsche21/VocalClaw_11Labs
cd VocalClaw_11Labs
pip install streamlit requests
streamlit run app.py
```

---

## Why This Wins

Most voice AI = one voice, one brain. Generic.

VocalClaw = 4 specialized agents, 4 distinct voices, free inference, spoken handoffs, and a Council Mode where agents literally debate your question out loud.

**Lex is a prototype of the world's first voice-native Indian legal AI** — built on real domain depth from JurixAI (backed by NSRCEL IIM Bangalore + Perplexity AI Fellowship).

---

## Built By

**Nick** — Founder, [JurixAI](https://jurixoneai.com)

Built in one night for the **ElevenLabs Agentic Summer Buildathon #1**

---

## License
MIT
