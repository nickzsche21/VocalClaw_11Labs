import streamlit as st
import requests
import base64
import json

ELEVENLABS_API_KEY = "sk_cabe7e77c8067fac91d6fde4bbc461b894f617353fc932a3"

AGENTS = {
    "Aria": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "role": "Orchestrator & General AI",
        "color": "#7C3AED",
        "emoji": "🎯",
        "description": "Routes your question to the right specialist"
    },
    "Rex": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Domi
        "role": "Code Specialist",
        "color": "#0EA5E9",
        "emoji": "💻",
        "description": "Programming, debugging, architecture"
    },
    "Lex": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
        "role": "Legal Specialist",
        "color": "#059669",
        "emoji": "⚖️",
        "description": "Legal research, statutes, case analysis"
    },
    "Max": {
        "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni
        "role": "Research Specialist",
        "color": "#D97706",
        "emoji": "🔬",
        "description": "General research, facts, deep dives"
    }
}

def detect_agent(question):
    q = question.lower()
    if any(w in q for w in ["code", "python", "javascript", "function", "bug", "error", "debug", "program", "script", "api", "database", "algorithm"]):
        return "Rex"
    elif any(w in q for w in ["law", "legal", "ipc", "section", "court", "statute", "act", "rights", "contract", "criminal", "civil", "judge", "advocate"]):
        return "Lex"
    elif any(w in q for w in ["research", "study", "explain", "what is", "how does", "why", "history", "science", "data", "compare", "difference"]):
        return "Max"
    else:
        return "Aria"

def generate_speech(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    return None

def get_agent_response(agent_name, question):
    responses = {
        "Aria": f"Hello! I'm Aria, your AI orchestrator. You asked: {question}. Let me help you with that directly. I coordinate all agents in the VocalClaw system and handle general queries like yours with precision.",
        "Rex": f"Hey, Rex here — code mode activated. Your question: {question}. From a technical standpoint, I'll break this down systematically. I specialize in software engineering, debugging, and architecture decisions.",
        "Lex": f"This is Lex, your legal specialist. Regarding your question — {question} — let me analyze this from a legal framework. I cover Indian law, IPC sections, civil and criminal statutes, and case precedents.",
        "Max": f"Max here, research mode on. You asked about: {question}. I'll synthesize the most relevant information for you. I specialize in deep research, factual analysis, and comprehensive explanations."
    }
    return responses[agent_name]

st.set_page_config(page_title="VocalClaw", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
.main-title { font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 0; }
.subtitle { text-align: center; color: #6B7280; margin-bottom: 2rem; font-size: 1rem; }
.agent-card { border-radius: 12px; padding: 1rem 1.25rem; margin: 0.5rem 0; border: 1px solid #E5E7EB; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.routing-banner { background: #F3F4F6; border-radius: 10px; padding: 1rem; text-align: center; margin: 1rem 0; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎙️ VocalClaw</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multi-Agent Voice AI · ElevenLabs × AirClaw · $0 LLM Cost</div>', unsafe_allow_html=True)

cols = st.columns(4)
for i, (name, info) in enumerate(AGENTS.items()):
    with cols[i]:
        st.markdown(f"""
        <div style="text-align:center; padding: 0.75rem; border-radius: 10px; border: 1px solid #E5E7EB;">
            <div style="font-size:1.5rem">{info['emoji']}</div>
            <div style="font-weight:600; color:{info['color']}">{name}</div>
            <div style="font-size:0.7rem; color:#6B7280">{info['role']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

question = st.text_area("💬 Ask anything — VocalClaw routes it to the right agent", 
                         placeholder="e.g. Explain IPC Section 302 · Write a Python parser · What caused WW2",
                         height=100)

col1, col2 = st.columns([3, 1])
with col1:
    ask_btn = st.button("🚀 Ask VocalClaw", use_container_width=True, type="primary")
with col2:
    manual_agent = st.selectbox("Force agent", ["Auto"] + list(AGENTS.keys()), label_visibility="collapsed")

if ask_btn and question.strip():
    if manual_agent == "Auto":
        chosen = detect_agent(question)
        routing_text = f"🧠 Aria is routing your question → **{chosen} {AGENTS[chosen]['emoji']}**"
    else:
        chosen = manual_agent
        routing_text = f"📌 Manually routed → **{chosen} {AGENTS[chosen]['emoji']}**"

    st.markdown(f'<div class="routing-banner">{routing_text}</div>', unsafe_allow_html=True)

    agent_info = AGENTS[chosen]
    response_text = get_agent_response(chosen, question)

    st.markdown(f"""
    <div style="background:{agent_info['color']}15; border-left: 4px solid {agent_info['color']}; 
    border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0;">
        <div style="font-weight:700; color:{agent_info['color']}; margin-bottom:0.5rem">
            {agent_info['emoji']} {chosen} — {agent_info['role']}
        </div>
        <div style="color:#1F2937; line-height:1.6">{response_text}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"🔊 Generating {chosen}'s voice via ElevenLabs..."):
        audio = generate_speech(response_text, agent_info["voice_id"])

    if audio:
        st.success(f"✅ Speaking as {chosen}")
        st.audio(audio, format="audio/mpeg")
    else:
        st.error("Voice generation failed — check API key or ElevenLabs credits")

elif ask_btn:
    st.warning("Type a question first!")

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#9CA3AF; font-size:0.8rem">
    Built for <b>ElevenLabs Agentic Summer Buildathon</b> · 
    ElevenLabs (voice) × AirClaw (local inference) · 
    <a href="https://github.com/nickzsche21/VocalClaw_11Labs" style="color:#7C3AED">GitHub</a>
</div>
""", unsafe_allow_html=True)
