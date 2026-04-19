"""
VocalClaw — Multi-Agent Voice AI
ElevenLabs handles voice. AirClaw handles thinking. $0 in LLM costs.
"""

import asyncio
import json
import os
import base64
import uuid
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx

# ─── Config ────────────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_cabe7e77c8067fac91d6fde4bbc461b894f617353fc932a3")
AIRCLAW_URL = os.getenv("AIRCLAW_URL", "http://localhost:4096/v1")

# ─── Agent Registry ─────────────────────────────────────────────────────────────
# Each agent = distinct personality + distinct ElevenLabs voice
AGENTS = {
    "aria": {
        "name": "Aria",
        "role": "Orchestrator & General Assistant",
        "emoji": "✦",
        "color": "#7c3aed",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel — warm, confident
        "voice_label": "Rachel",
        "system": """You are Aria, the lead agent in VocalClaw — a multi-agent voice AI system powered by local LLM inference via AirClaw.

You are the orchestrator. You handle general queries and route specialized work to your team:
- REX handles: code, debugging, technical questions, programming
- LEX handles: legal questions, contracts, compliance, regulations  
- MAX handles: research, factual lookups, web information, data

To route to a specialist, start your response with exactly: ROUTE:rex or ROUTE:lex or ROUTE:max
Then add a brief handoff note like: "Let me pass you to Rex for the technical side."

If you handle it yourself, just respond naturally. Keep responses conversational and concise — this is voice output. No markdown, no bullet points. Max 3 sentences unless depth is needed."""
    },
    "rex": {
        "name": "Rex",
        "role": "Code & Technical Specialist",
        "emoji": "⚡",
        "color": "#0ea5e9",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Domi — sharp, precise
        "voice_label": "Domi",
        "system": """You are Rex, the code and technical specialist in the VocalClaw agent team. You're precise, direct, and sharp.

You handle: programming questions, debugging, system design, technical explanations, DevOps, APIs.

Your responses are for voice output — be clear but concise. No markdown. No code fences in voice mode (say 'open bracket' etc. if needed). Give the core answer first, then explain if needed. Max 4 sentences."""
    },
    "lex": {
        "name": "Lex",
        "role": "Legal Intelligence Specialist",
        "emoji": "⚖",
        "color": "#10b981",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella — authoritative, professional
        "voice_label": "Bella",
        "system": """You are Lex, the legal intelligence specialist in the VocalClaw agent team. You're authoritative but approachable.

You handle: legal questions, contract review, compliance, regulations, legal strategy, Indian law, corporate law.

Your responses are for voice output — precise, structured, professional. No markdown. Always note when professional legal advice is needed. Max 4 sentences. End legal opinions with a brief disclaimer."""
    },
    "max": {
        "name": "Max",
        "role": "Research & Information Specialist",
        "emoji": "◎",
        "color": "#f59e0b",
        "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni — curious, engaging
        "voice_label": "Antoni",
        "system": """You are Max, the research and information specialist in the VocalClaw agent team. You're curious, thorough, and engaging.

You handle: factual questions, research summaries, current events (to your knowledge cutoff), comparisons, explanations of complex topics.

Your responses are for voice output — informative but conversational. No markdown. Lead with the key fact, then context. Max 4 sentences."""
    }
}

# ─── In-memory sessions ─────────────────────────────────────────────────────────
sessions: dict[str, dict] = {}

app = FastAPI(title="VocalClaw", version="1.0.0")

# ─── LLM Bridge ─────────────────────────────────────────────────────────────────
async def call_local_llm(messages: list[dict], system: str) -> str:
    """Route to AirClaw local LLM (OpenAI-compatible API)"""
    full_messages = [{"role": "system", "content": system}] + messages[-12:]

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{AIRCLAW_URL}/chat/completions",
                json={
                    "model": "local",
                    "messages": full_messages,
                    "temperature": 0.75,
                    "max_tokens": 350,
                    "stream": False,
                },
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                return f"AirClaw returned {response.status_code}. Make sure you ran 'airclaw start'."
    except httpx.ConnectError:
        return "AirClaw isn't running yet. Start it with 'airclaw start' in a terminal. I'm Aria, and I'm ready to think once the local model is online."
    except Exception as e:
        return f"Local LLM error: {str(e)[:100]}"


# ─── ElevenLabs Voice Layer ──────────────────────────────────────────────────────
async def transcribe_audio(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    """ElevenLabs Scribe STT"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                files={"file": ("audio.webm", audio_bytes, mime)},
                data={"model_id": "scribe_v1", "language_code": "en"}
            )
            if response.status_code == 200:
                return response.json().get("text", "").strip()
            return ""
    except Exception as e:
        return ""


async def synthesize_speech(text: str, voice_id: str) -> bytes:
    """ElevenLabs TTS — turbo model for speed"""
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.80,
                        "style": 0.1,
                        "speed": 1.05
                    }
                }
            )
            if response.status_code == 200:
                return response.content
            return b""
    except Exception:
        return b""


# ─── Agent Routing Logic ─────────────────────────────────────────────────────────
def parse_route(text: str) -> Optional[str]:
    """Check if LLM wants to route to another agent"""
    for key in AGENTS:
        tag = f"ROUTE:{key}"
        if tag in text:
            return key
    return None


async def run_agent_turn(
    websocket: WebSocket,
    session_id: str,
    user_text: str,
    active_agent_key: str
) -> str:
    """Process one turn through the agent system. Returns final response text."""
    session = sessions[session_id]
    agent = AGENTS[active_agent_key]

    # Add user message
    session["history"].append({"role": "user", "content": user_text})

    await websocket.send_json({
        "type": "thinking",
        "agent": active_agent_key,
        "agent_name": agent["name"]
    })

    # Call local LLM
    llm_response = await call_local_llm(session["history"], agent["system"])

    # Check for routing intent
    route_to = parse_route(llm_response)

    if route_to and route_to in AGENTS and route_to != active_agent_key:
        new_agent = AGENTS[route_to]

        # Notify UI about handoff
        handoff_msg = llm_response.split(f"ROUTE:{route_to}", 1)[-1].strip() or f"Passing you to {new_agent['name']}."
        
        await websocket.send_json({
            "type": "handoff",
            "from_key": active_agent_key,
            "to_key": route_to,
            "from_name": agent["name"],
            "to_name": new_agent["name"],
            "handoff_note": handoff_msg
        })

        # Synthesize handoff voice
        handoff_audio = await synthesize_speech(handoff_msg, agent["voice_id"])
        if handoff_audio:
            await websocket.send_json({
                "type": "audio",
                "audio": base64.b64encode(handoff_audio).decode(),
                "agent_key": active_agent_key
            })

        # Update session agent
        session["active_agent"] = route_to
        session["history"].append({"role": "assistant", "content": handoff_msg})

        # Now route to specialist
        await websocket.send_json({
            "type": "thinking",
            "agent": route_to,
            "agent_name": new_agent["name"]
        })

        specialist_response = await call_local_llm(
            session["history"],
            new_agent["system"]
        )
        session["history"].append({"role": "assistant", "content": specialist_response})

        return route_to, specialist_response

    else:
        session["history"].append({"role": "assistant", "content": llm_response})
        return active_agent_key, llm_response


# ─── WebSocket Handler ───────────────────────────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def ws_handler(websocket: WebSocket, session_id: str):
    await websocket.accept()

    sessions[session_id] = {
        "history": [],
        "active_agent": "aria"
    }

    await websocket.send_json({
        "type": "ready",
        "agent": "aria",
        "agents": {k: {"name": v["name"], "role": v["role"], "color": v["color"], "emoji": v["emoji"]} for k, v in AGENTS.items()}
    })

    try:
        while True:
            raw = await websocket.receive_json()
            msg_type = raw.get("type")
            session = sessions[session_id]

            # ── Voice input ──
            if msg_type == "audio":
                audio_b64 = raw.get("audio", "")
                audio_bytes = base64.b64decode(audio_b64)

                await websocket.send_json({"type": "status", "msg": "Transcribing your voice..."})
                user_text = await transcribe_audio(audio_bytes)

                if not user_text:
                    await websocket.send_json({"type": "status", "msg": "Couldn't catch that — try again."})
                    continue

                await websocket.send_json({"type": "user_text", "text": user_text})

            # ── Text input (fallback / debug) ──
            elif msg_type == "text":
                user_text = raw.get("text", "").strip()
                if not user_text:
                    continue
                await websocket.send_json({"type": "user_text", "text": user_text})

            # ── Manual agent select ──
            elif msg_type == "select_agent":
                new_key = raw.get("agent")
                if new_key in AGENTS:
                    session["active_agent"] = new_key
                    await websocket.send_json({"type": "agent_active", "agent": new_key})
                continue

            else:
                continue

            # ── Agent turn ──
            active_agent_key = session.get("active_agent", "aria")
            final_agent_key, response_text = await run_agent_turn(
                websocket, session_id, user_text, active_agent_key
            )
            final_agent = AGENTS[final_agent_key]

            # Send text response
            await websocket.send_json({
                "type": "response",
                "text": response_text,
                "agent_key": final_agent_key,
                "agent_name": final_agent["name"],
                "agent_color": final_agent["color"]
            })

            # Synthesize and send voice
            await websocket.send_json({"type": "status", "msg": f"{final_agent['name']} is speaking..."})
            audio_bytes = await synthesize_speech(response_text, final_agent["voice_id"])

            if audio_bytes:
                await websocket.send_json({
                    "type": "audio",
                    "audio": base64.b64encode(audio_bytes).decode(),
                    "agent_key": final_agent_key
                })
            
            await websocket.send_json({"type": "idle"})

    except WebSocketDisconnect:
        sessions.pop(session_id, None)
    except Exception as e:
        await websocket.send_json({"type": "error", "msg": str(e)})
        sessions.pop(session_id, None)


# ─── Static ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def index():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health():
    return {"status": "ok", "agents": list(AGENTS.keys()), "airclaw_url": AIRCLAW_URL}
