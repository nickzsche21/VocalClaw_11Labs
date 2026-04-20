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
        "system": "You are Aria, an intelligent AI orchestrator. You are sharp, warm, and confident. Answer clearly in 2-3 sentences max.",
        "keywords": []
    },
    "Rex": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "color": "#38BDF8",
        "emoji": "💻",
        "role": "Code Specialist",
        "system": "You are Rex, an elite software engineer. Be direct and technical. Include short code snippets when helpful. Max 3-4 sentences.",
        "keywords": ["code", "python", "javascript", "function", "bug", "error", "debug", "program", "script", "api", "database", "algorithm", "syntax", "class", "loop", "array", "compile", "runtime", "git", "deploy", "react", "css", "html"]
    },
    "Lex": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "color": "#34D399",
        "emoji": "⚖️",
        "role": "Legal Specialist",
        "system": "You are Lex, a brilliant legal specialist in Indian law. Be precise and authoritative. Cite IPC, CrPC, and case law when relevant. Max 3-4 sentences.",
        "keywords": ["law", "legal", "ipc", "section", "court", "statute", "act", "rights", "contract", "criminal", "civil", "judge", "advocate", "petition", "bail", "verdict", "constitution", "crpc", "fir", "arrest", "offence", "punishment"]
    },
    "Max": {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "color": "#FB923C",
        "emoji": "🔬",
        "role": "Research Specialist",
        "system": "You are Max, a deep research specialist. Synthesize complex topics into clear, fascinating insights. Cover science, history, tech, business. Max 3-4 sentences.",
        "keywords": ["research", "explain", "what is", "how does", "why", "history", "science", "data", "compare", "difference", "study", "facts", "tell me about", "who is", "when did", "where is"]
    }
}

GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]

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
    for model in GROQ_MODELS:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": agent["system"]},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"], model
        except Exception:
            continue
    return None, None

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
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; margin: 0; }

.stApp { background: #06060A !important; }

.block-container {
    max-width: 740px !important;
    padding: 2rem 1.5rem 4rem !important;
}

/* ── HERO ── */
.hero-wrap { text-align: center; padding: 3rem 0 2rem; }

.hero-eyebrow {
    display: inline-block;
    border: 1px solid rgba(167,139,250,0.22);
    background: rgba(167,139,250,0.07);
    color: #A78BFA !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    padding: 5px 16px;
    border-radius: 4px;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: clamp(4.5rem, 14vw, 7.5rem);
    letter-spacing: 0.06em;
    line-height: 0.92;
    margin: 0 0 0.6rem;
    background: linear-gradient(160deg, #ffffff 30%, #A78BFA 65%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-tagline {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.28) !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

.divider-line {
    width: 40px;
    height: 1px;
    background: rgba(167,139,250,0.35);
    margin: 1.2rem auto;
}

/* ── STATS ── */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-bottom: 2.8rem;
}
.stat-block { text-align: center; }
.stat-n {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.4rem;
    letter-spacing: 0.04em;
    display: block;
    line-height: 1;
}
.stat-l {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    color: rgba(255,255,255,0.25) !important;
    text-transform: uppercase;
    margin-top: 3px;
    display: block;
}

/* ── AGENT GRID ── */
.agents-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 2rem;
}
.agent-tile {
    background: rgba(255,255,255,0.022);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 10px;
    padding: 1rem 0.5rem 0.9rem;
    text-align: center;
    position: relative;
}
.agent-tile-top {
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    border-radius: 1px;
}
.agent-tile .icon { font-size: 1.4rem; display: block; margin-bottom: 0.35rem; }
.agent-tile .name {
    font-family: 'Barlow', sans-serif !important;
    font-weight: 600;
    font-size: 0.9rem;
    display: block;
}
.agent-tile .role-lbl {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem;
    color: rgba(255,255,255,0.25) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 2px;
    display: block;
}

/* ── INPUT ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #F0EFF5 !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
    line-height: 1.6 !important;
}
.stTextArea textarea:focus {
    border-color: rgba(167,139,250,0.4) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.07) !important;
}
.stTextArea textarea::placeholder { color: rgba(240,239,245,0.18) !important; }
.stTextArea label { display: none !important; }

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #6D28D9, #4338CA) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Barlow', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.62rem 1.4rem !important;
    box-shadow: 0 4px 20px rgba(109,40,217,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(109,40,217,0.45) !important;
}

/* ── SELECT ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #F0EFF5 !important;
    font-family: 'Barlow', sans-serif !important;
}
.stSelectbox svg { fill: rgba(240,239,245,0.35) !important; }
.stSelectbox label { display: none !important; }

/* ── ROUTING ── */
.routing-chip {
    background: rgba(167,139,250,0.07);
    border: 1px solid rgba(167,139,250,0.16);
    border-radius: 8px;
    padding: 0.7rem 1.1rem;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    color: rgba(240,239,245,0.5) !important;
    letter-spacing: 0.06em;
    margin: 0.8rem 0;
    text-align: center;
}

/* ── RESPONSE ── */
.res-card {
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    margin: 0.8rem 0;
}
.res-card.aria { background: rgba(167,139,250,0.055); border: 1px solid rgba(167,139,250,0.13); border-left: 3px solid #A78BFA; }
.res-card.rex  { background: rgba(56,189,248,0.055);  border: 1px solid rgba(56,189,248,0.13);  border-left: 3px solid #38BDF8; }
.res-card.lex  { background: rgba(52,211,153,0.055);  border: 1px solid rgba(52,211,153,0.13);  border-left: 3px solid #34D399; }
.res-card.max  { background: rgba(251,146,60,0.055);  border: 1px solid rgba(251,146,60,0.13);  border-left: 3px solid #FB923C; }

.res-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    margin-bottom: 0.6rem;
    display: block;
}
.res-label.aria { color: #A78BFA !important; }
.res-label.rex  { color: #38BDF8 !important; }
.res-label.lex  { color: #34D399 !important; }
.res-label.max  { color: #FB923C !important; }

.res-text {
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.95rem;
    line-height: 1.75;
    color: rgba(240,239,245,0.8) !important;
}

.voice-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.18);
    color: #34D399 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.64rem;
    padding: 3px 11px;
    border-radius: 4px;
    letter-spacing: 0.07em;
    margin: 0.7rem 0 0.4rem;
}

.error-chip {
    background: rgba(239,68,68,0.07);
    border: 1px solid rgba(239,68,68,0.18);
    color: #F87171 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    margin: 0.8rem 0;
}

/* ── FOOTER ── */
.footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.footer-text {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem;
    color: rgba(255,255,255,0.16) !important;
    letter-spacing: 0.1em;
    line-height: 2;
}
.footer-text a { color: rgba(167,139,250,0.4) !important; text-decoration: none; margin: 0 0.5rem; }

#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⚡ ElevenLabs × Groq × AirClaw · Agentic Summer Buildathon</div>
    <div class="hero-title">VocalClaw</div>
    <div class="divider-line"></div>
    <div class="hero-tagline">Multi-Agent Voice AI &nbsp;·&nbsp; $0 LLM Cost &nbsp;·&nbsp; Real-Time Intelligence</div>
    <div class="stats-row">
        <div class="stat-block"><span class="stat-n" style="color:#A78BFA">4</span><span class="stat-l">Agents</span></div>
        <div class="stat-block"><span class="stat-n" style="color:#38BDF8">4</span><span class="stat-l">Voices</span></div>
        <div class="stat-block"><span class="stat-n" style="color:#34D399">$0</span><span class="stat-l">LLM Cost</span></div>
        <div class="stat-block"><span class="stat-n" style="color:#FB923C">∞</span><span class="stat-l">Queries</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# AGENTS
st.markdown("""
<div class="agents-grid">
    <div class="agent-tile">
        <div class="agent-tile-top" style="background:#A78BFA"></div>
        <span class="icon">🎯</span>
        <span class="name" style="color:#A78BFA">Aria</span>
        <span class="role-lbl">Orchestrator</span>
    </div>
    <div class="agent-tile">
        <div class="agent-tile-top" style="background:#38BDF8"></div>
        <span class="icon">💻</span>
        <span class="name" style="color:#38BDF8">Rex</span>
        <span class="role-lbl">Code</span>
    </div>
    <div class="agent-tile">
        <div class="agent-tile-top" style="background:#34D399"></div>
        <span class="icon">⚖️</span>
        <span class="name" style="color:#34D399">Lex</span>
        <span class="role-lbl">Legal</span>
    </div>
    <div class="agent-tile">
        <div class="agent-tile-top" style="background:#FB923C"></div>
        <span class="icon">🔬</span>
        <span class="name" style="color:#FB923C">Max</span>
        <span class="role-lbl">Research</span>
    </div>
</div>
""", unsafe_allow_html=True)

# INPUT
question = st.text_area(
    "q",
    placeholder="Try: 'Explain IPC Section 302'  ·  'Write a Python parser'  ·  'What caused the 2008 crash'",
    height=105,
    label_visibility="collapsed"
)

c1, c2 = st.columns([3, 1])
with c1:
    ask = st.button("⚡  Ask VocalClaw", use_container_width=True)
with c2:
    manual = st.selectbox("a", ["Auto"] + list(AGENTS.keys()), label_visibility="collapsed")

# RESPONSE
if ask and question.strip():
    chosen = manual if manual != "Auto" else detect_agent(question)
    agent = AGENTS[chosen]
    cls = chosen.lower()

    if manual == "Auto":
        st.markdown(f"""
        <div class="routing-chip">
            🧠 Aria routing → <strong style="color:{agent['color']}">{agent['emoji']} {chosen}</strong> · {agent['role']}
        </div>
        """, unsafe_allow_html=True)

    with st.spinner(f"{chosen} thinking..."):
        text, model_used = get_groq_response(chosen, question)

    if text:
        st.markdown(f"""
        <div class="res-card {cls}">
            <span class="res-label {cls}">{agent['emoji']} {chosen.upper()} — {agent['role'].upper()}</span>
            <div class="res-text">{text}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(f"Generating {chosen}'s voice..."):
            audio = generate_speech(text, agent["voice_id"])

        if audio:
            st.markdown(f'<div class="voice-chip">🔊 Speaking as {chosen} via ElevenLabs</div>', unsafe_allow_html=True)
            st.audio(audio, format="audio/mpeg")
        else:
            st.markdown('<div class="error-chip">⚠ Voice generation failed — check ElevenLabs credits</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-chip">⚠ Groq API unavailable — all models failed. Check API key or try again.</div>', unsafe_allow_html=True)

elif ask:
    st.warning("Type something first!")

# FOOTER
st.markdown("""
<div class="footer">
    <div class="footer-text">
        BUILT FOR ELEVENLABS AGENTIC SUMMER BUILDATHON<br>
        ELEVENLABS VOICE × GROQ INFERENCE × AIRCLAW LOCAL
        <br>
        <a href="https://github.com/nickzsche21/VocalClaw_11Labs">GitHub ↗</a>
        <a href="https://elevenlabs.io">ElevenLabs ↗</a>
        <a href="https://groq.com">Groq ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)
