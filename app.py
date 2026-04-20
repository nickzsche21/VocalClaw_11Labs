import streamlit as st
import requests

ELEVENLABS_API_KEY = "sk_cabe7e77c8067fac91d6fde4bbc461b894f617353fc932a3"
GROQ_API_KEY = "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"

AGENTS = {
    "Aria": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "color": "#A78BFA",
        "emoji": "🎯",
        "role": "Orchestrator",
        "system": "You are Aria, an intelligent AI orchestrator and general assistant. You are sharp, warm, and confident. Answer clearly and concisely in 2-3 sentences max. You coordinate a team of specialists: Rex (code), Lex (legal), Max (research).",
        "keywords": []
    },
    "Rex": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "color": "#38BDF8",
        "emoji": "💻",
        "role": "Code Specialist",
        "system": "You are Rex, an elite software engineer. You speak in a direct, technical, no-nonsense style. Answer coding questions with precision. Include short code snippets when helpful. Keep answers under 4 sentences.",
        "keywords": ["code", "python", "javascript", "function", "bug", "error", "debug", "program", "script", "api", "database", "algorithm", "syntax", "class", "loop", "array", "compile", "runtime", "git", "deploy"]
    },
    "Lex": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "color": "#34D399",
        "emoji": "⚖️",
        "role": "Legal Specialist",
        "system": "You are Lex, a brilliant legal specialist focusing on Indian law. You are precise, authoritative, and cite relevant statutes when applicable. Cover IPC, CrPC, constitutional law, contracts, and case precedents. Keep answers under 4 sentences.",
        "keywords": ["law", "legal", "ipc", "section", "court", "statute", "act", "rights", "contract", "criminal", "civil", "judge", "advocate", "petition", "bail", "verdict", "constitution", "crpc", "fir", "arrest"]
    },
    "Max": {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "color": "#FB923C",
        "emoji": "🔬",
        "role": "Research Specialist",
        "system": "You are Max, a deep research specialist with encyclopedic knowledge. You synthesize complex topics into clear insights. You cover science, history, technology, business, and current events. Keep answers under 4 sentences.",
        "keywords": ["research", "explain", "what is", "how does", "why", "history", "science", "data", "compare", "difference", "study", "analysis", "facts", "tell me about"]
    }
}

def detect_agent(question):
    q = question.lower()
    for name, info in AGENTS.items():
        if name == "Aria":
            continue
        if any(w in q for w in info["keywords"]):
            return name
    return "Aria"

def get_groq_response(agent_name, question):
    agent = AGENTS[agent_name]
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": agent["system"]},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=15
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return "I encountered an error processing your request. Please try again."

def generate_speech(text, voice_id):
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            },
            timeout=20
        )
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

st.set_page_config(page_title="VocalClaw", page_icon="🎙️", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #050508 !important;
    font-family: 'Syne', sans-serif;
}

.block-container {
    max-width: 760px !important;
    padding: 2rem 1.5rem 4rem !important;
}

h1,h2,h3,p,label,div,span { font-family: 'Syne', sans-serif; }

.hero-badge {
    display: inline-block;
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.25);
    color: #A78BFA !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    padding: 5px 16px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
}

.hero-title {
    font-size: 5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0 0 0.4rem;
    background: linear-gradient(135deg, #ffffff 0%, #A78BFA 45%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    color: rgba(241,240,245,0.35) !important;
    letter-spacing: 0.12em;
    margin-bottom: 2.5rem;
}

.stats-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-bottom: 2.5rem;
}

.stat-num { font-size: 2rem; font-weight: 800; display: block; line-height: 1; }
.stat-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem;
    color: rgba(241,240,245,0.3) !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    display: block;
    margin-top: 2px;
}

.agents-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 2rem;
}

.agent-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1rem 0.6rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.agent-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 2px 2px 0 0;
}
.agent-card.aria::after { background: linear-gradient(90deg, #A78BFA, transparent); }
.agent-card.rex::after  { background: linear-gradient(90deg, #38BDF8, transparent); }
.agent-card.lex::after  { background: linear-gradient(90deg, #34D399, transparent); }
.agent-card.max::after  { background: linear-gradient(90deg, #FB923C, transparent); }

.agent-icon { font-size: 1.5rem; display: block; margin-bottom: 0.3rem; }
.agent-name { font-weight: 700; font-size: 0.9rem; display: block; }
.agent-name.aria { color: #A78BFA !important; }
.agent-name.rex  { color: #38BDF8 !important; }
.agent-name.lex  { color: #34D399 !important; }
.agent-name.max  { color: #FB923C !important; }
.agent-role-label { font-family: 'JetBrains Mono', monospace !important; font-size: 0.58rem; color: rgba(241,240,245,0.3) !important; display: block; margin-top: 2px; }

.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
    color: #F1F0F5 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(167,139,250,0.45) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.08) !important;
}
.stTextArea textarea::placeholder { color: rgba(241,240,245,0.2) !important; }
.stTextArea label { color: rgba(241,240,245,0.0) !important; font-size: 0 !important; }

.stButton > button {
    background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.5) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    color: #F1F0F5 !important;
}
.stSelectbox svg { fill: rgba(241,240,245,0.4) !important; }

.routing-pill {
    display: inline-block;
    background: rgba(167,139,250,0.08);
    border: 1px solid rgba(167,139,250,0.18);
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem;
    color: rgba(241,240,245,0.6) !important;
    margin: 0.8rem 0;
    letter-spacing: 0.04em;
    width: 100%;
    text-align: center;
}

.response-wrap {
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin: 0.8rem 0;
    position: relative;
}
.response-wrap.aria { background: rgba(167,139,250,0.06); border: 1px solid rgba(167,139,250,0.14); border-left: 3px solid #A78BFA; }
.response-wrap.rex  { background: rgba(56,189,248,0.06);  border: 1px solid rgba(56,189,248,0.14);  border-left: 3px solid #38BDF8; }
.response-wrap.lex  { background: rgba(52,211,153,0.06);  border: 1px solid rgba(52,211,153,0.14);  border-left: 3px solid #34D399; }
.response-wrap.max  { background: rgba(251,146,60,0.06);  border: 1px solid rgba(251,146,60,0.14);  border-left: 3px solid #FB923C; }

.response-agent-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
    display: block;
}
.response-agent-label.aria { color: #A78BFA !important; }
.response-agent-label.rex  { color: #38BDF8 !important; }
.response-agent-label.lex  { color: #34D399 !important; }
.response-agent-label.max  { color: #FB923C !important; }

.response-body {
    font-size: 0.95rem;
    line-height: 1.75;
    color: rgba(241,240,245,0.82) !important;
}

.voice-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.2);
    color: #34D399 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.67rem;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    margin: 0.75rem 0 0.4rem;
}

.footer-wrap {
    text-align: center;
    margin-top: 3.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.footer-mono {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem;
    color: rgba(241,240,245,0.18) !important;
    letter-spacing: 0.1em;
}
.footer-mono a { color: rgba(167,139,250,0.45) !important; text-decoration: none; margin: 0 0.6rem; }

#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2.5rem 0 1.5rem;">
    <div class="hero-badge">⚡ ElevenLabs × Groq × AirClaw · Agentic Summer Buildathon</div>
    <div class="hero-title">VocalClaw</div>
    <div class="hero-sub">MULTI-AGENT VOICE AI · $0 LLM COST · REAL-TIME INTELLIGENCE</div>
    <div class="stats-row">
        <div><span class="stat-num" style="color:#A78BFA">4</span><span class="stat-label">Agents</span></div>
        <div><span class="stat-num" style="color:#38BDF8">4</span><span class="stat-label">Voices</span></div>
        <div><span class="stat-num" style="color:#34D399">$0</span><span class="stat-label">LLM Cost</span></div>
        <div><span class="stat-num" style="color:#FB923C">∞</span><span class="stat-label">Queries</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── AGENTS GRID ───────────────────────────────────────
st.markdown("""
<div class="agents-grid">
    <div class="agent-card aria">
        <span class="agent-icon">🎯</span>
        <span class="agent-name aria">Aria</span>
        <span class="agent-role-label">Orchestrator</span>
    </div>
    <div class="agent-card rex">
        <span class="agent-icon">💻</span>
        <span class="agent-name rex">Rex</span>
        <span class="agent-role-label">Code</span>
    </div>
    <div class="agent-card lex">
        <span class="agent-icon">⚖️</span>
        <span class="agent-name lex">Lex</span>
        <span class="agent-role-label">Legal</span>
    </div>
    <div class="agent-card max">
        <span class="agent-icon">🔬</span>
        <span class="agent-name max">Max</span>
        <span class="agent-role-label">Research</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────
question = st.text_area(
    "q",
    placeholder="Try: 'Explain IPC Section 302' · 'Write a Python web scraper' · 'What caused the 2008 financial crisis'",
    height=110,
    label_visibility="collapsed"
)

c1, c2 = st.columns([3, 1])
with c1:
    ask = st.button("⚡  Ask VocalClaw", use_container_width=True)
with c2:
    manual = st.selectbox("a", ["Auto"] + list(AGENTS.keys()), label_visibility="collapsed")

# ── RESPONSE ──────────────────────────────────────────
if ask and question.strip():
    chosen = manual if manual != "Auto" else detect_agent(question)
    agent = AGENTS[chosen]
    cls = chosen.lower()

    if manual == "Auto":
        st.markdown(f"""
        <div class="routing-pill">
            🧠 Aria routing → <strong style="color:{agent['color']}">{agent['emoji']} {chosen}</strong> · {agent['role']}
        </div>
        """, unsafe_allow_html=True)

    with st.spinner(f"{chosen} thinking..."):
        text = get_groq_response(chosen, question)

    st.markdown(f"""
    <div class="response-wrap {cls}">
        <span class="response-agent-label {cls}">{agent['emoji']} {chosen.upper()} — {agent['role'].upper()}</span>
        <div class="response-body">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Generating {chosen}'s voice..."):
        audio = generate_speech(text, agent["voice_id"])

    if audio:
        st.markdown(f'<div class="voice-tag">🔊 Speaking as {chosen} via ElevenLabs</div>', unsafe_allow_html=True)
        st.audio(audio, format="audio/mpeg")
    else:
        st.error("Voice generation failed — check ElevenLabs credits")

elif ask:
    st.warning("Type something first!")

# ── FOOTER ────────────────────────────────────────────
st.markdown("""
<div class="footer-wrap">
    <div class="footer-mono">
        BUILT FOR ELEVENLABS AGENTIC SUMMER BUILDATHON · ELEVENLABS VOICE × GROQ INFERENCE × AIRCLAW LOCAL
        <br/><br/>
        <a href="https://github.com/nickzsche21/VocalClaw_11Labs">GitHub ↗</a>
        <a href="https://elevenlabs.io">ElevenLabs ↗</a>
        <a href="https://groq.com">Groq ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)
