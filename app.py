import streamlit as st
import requests
import json

# ── KEYS ──────────────────────────────────────────────────────────────────────
EL_KEY   = "sk_cabe7e77c8067fac91d6fde4bbc461b894f617353fc932a3"
GROQ_KEY = "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"

# ── AGENTS ────────────────────────────────────────────────────────────────────
AGENTS = {
    "Aria": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "color": "#A78BFA", "cls": "aria", "emoji": "🎯",
        "role": "Orchestrator",
        "system": "You are Aria, an intelligent AI orchestrator. You are warm, sharp, and confident. Answer in 2-3 concise sentences. When routing, say something like 'Let me hand you to Rex for that.' Keep it natural.",
        "keywords": []
    },
    "Rex": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "color": "#38BDF8", "cls": "rex", "emoji": "💻",
        "role": "Code Specialist",
        "system": "You are Rex, an elite software engineer. Be direct, technical, no fluff. Give precise answers with code snippets when relevant. Max 3-4 sentences.",
        "keywords": ["code","python","javascript","function","bug","error","debug","program","script","api","database","algorithm","syntax","class","loop","array","compile","runtime","git","deploy","react","css","html","java","typescript","sql"]
    },
    "Lex": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "color": "#34D399", "cls": "lex", "emoji": "⚖️",
        "role": "Legal Specialist",
        "system": "You are Lex, a brilliant Indian legal specialist. Be authoritative, precise, cite IPC/CrPC/Constitution when relevant. Max 3-4 sentences.",
        "keywords": ["law","legal","ipc","section","court","statute","act","rights","contract","criminal","civil","judge","advocate","petition","bail","verdict","constitution","crpc","fir","arrest","offence","punishment","lawyer","case","judgment"]
    },
    "Max": {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "color": "#FB923C", "cls": "max", "emoji": "🔬",
        "role": "Research Specialist",
        "system": "You are Max, a deep research specialist with encyclopedic knowledge. Synthesize complex ideas into clear, fascinating insights. Max 3-4 sentences.",
        "keywords": ["research","explain","what is","how does","why","history","science","data","compare","difference","study","facts","tell me","who is","when did","where is","what happened","economics","politics","medicine","physics","biology"]
    }
}

GROQ_MODELS = ["llama-3.1-8b-instant","llama3-8b-8192","mixtral-8x7b-32768","gemma-7b-it"]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def detect_agent(text):
    t = text.lower()
    for name, info in AGENTS.items():
        if name == "Aria": continue
        if any(w in t for w in info["keywords"]):
            return name
    return "Aria"

def groq(agent_name, question, context=""):
    system = AGENTS[agent_name]["system"]
    if context:
        system += f"\n\nConversation context: {context}"
    for model in GROQ_MODELS:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": question}
                ], "max_tokens": 180, "temperature": 0.75},
                timeout=20
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except: continue
    return None

def tts(text, voice_id):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": EL_KEY, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_monolingual_v1",
                  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
            timeout=20
        )
        return r.content if r.status_code == 200 else None
    except: return None

def scribe_stt(audio_bytes):
    try:
        r = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": EL_KEY},
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"model_id": "scribe_v1"},
            timeout=30
        )
        if r.status_code == 200:
            return r.json().get("text","").strip()
    except: pass
    return None

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="VocalClaw", page_icon="🎙️", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }
.stApp { background: #07070C !important; }
.block-container { max-width: 760px !important; padding: 1.5rem 1.5rem 4rem !important; }

/* ── HERO ── */
.vc-badge {
    display: inline-block;
    border: 1px solid rgba(167,139,250,0.2);
    background: rgba(167,139,250,0.06);
    color: #A78BFA !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem; letter-spacing: 0.18em;
    padding: 4px 14px; border-radius: 3px;
    text-transform: uppercase; margin-bottom: 1rem;
}
.vc-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: clamp(4rem, 12vw, 6.5rem);
    letter-spacing: 0.05em; line-height: 0.9;
    background: linear-gradient(150deg, #fff 20%, #A78BFA 60%, #38BDF8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.4rem;
}
.vc-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem; letter-spacing: 0.16em;
    color: rgba(255,255,255,0.22) !important;
    text-transform: uppercase; margin-bottom: 0.5rem;
}
.vc-divider { width: 36px; height: 1px; background: rgba(167,139,250,0.3); margin: 1rem auto 1.6rem; }

/* ── STATS ── */
.vc-stats { display: flex; justify-content: center; gap: 2.5rem; margin-bottom: 2rem; }
.vc-stat-n { font-family: 'Bebas Neue', sans-serif !important; font-size: 2.2rem; letter-spacing: 0.04em; display: block; line-height: 1; }
.vc-stat-l { font-family: 'JetBrains Mono', monospace !important; font-size: 0.55rem; letter-spacing: 0.14em; color: rgba(255,255,255,0.22) !important; text-transform: uppercase; display: block; margin-top: 2px; }

/* ── AGENTS ── */
.vc-agents { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 1.8rem; }
.vc-agent {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px; padding: 0.9rem 0.4rem; text-align: center; position: relative;
}
.vc-agent-bar { position: absolute; top:0; left:15%; right:15%; height:1px; border-radius:1px; }
.vc-agent-icon { font-size: 1.35rem; display: block; margin-bottom: 0.25rem; }
.vc-agent-name { font-family: 'Barlow', sans-serif !important; font-weight: 700; font-size: 0.88rem; display: block; }
.vc-agent-role { font-family: 'JetBrains Mono', monospace !important; font-size: 0.54rem; color: rgba(255,255,255,0.22) !important; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-top: 1px; }

/* ── MODE TABS ── */
.vc-modes { display: flex; gap: 8px; margin-bottom: 1.2rem; }
.vc-mode {
    flex: 1; border-radius: 8px; padding: 0.7rem 1rem; text-align: center; cursor: pointer;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.7rem; letter-spacing: 0.08em;
    border: 1px solid rgba(255,255,255,0.07); background: rgba(255,255,255,0.02);
    color: rgba(255,255,255,0.35) !important; text-transform: uppercase;
}
.vc-mode.active-solo  { background: rgba(167,139,250,0.1); border-color: rgba(167,139,250,0.3); color: #A78BFA !important; }
.vc-mode.active-council { background: rgba(251,146,60,0.1); border-color: rgba(251,146,60,0.3); color: #FB923C !important; }

/* ── INPUT ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important; color: #F0EEF8 !important;
    font-family: 'Barlow', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.9rem !important; line-height: 1.6 !important;
}
.stTextArea textarea:focus { border-color: rgba(167,139,250,0.38) !important; box-shadow: 0 0 0 3px rgba(167,139,250,0.06) !important; }
.stTextArea textarea::placeholder { color: rgba(240,238,248,0.17) !important; }
.stTextArea label { display: none !important; }

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #6D28D9, #4338CA) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-family: 'Barlow', sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; letter-spacing: 0.03em !important;
    padding: 0.6rem 1.2rem !important; box-shadow: 0 4px 18px rgba(109,40,217,0.28) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 26px rgba(109,40,217,0.42) !important; }

/* ── SELECT ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important; color: #F0EEF8 !important;
    font-family: 'Barlow', sans-serif !important;
}
.stSelectbox svg { fill: rgba(240,238,248,0.3) !important; }
.stSelectbox label { color: rgba(240,238,248,0.35) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.1em; text-transform: uppercase; }

/* ── ROUTING ── */
.vc-routing {
    background: rgba(167,139,250,0.06); border: 1px solid rgba(167,139,250,0.14);
    border-radius: 8px; padding: 0.65rem 1rem;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.7rem;
    color: rgba(240,238,248,0.45) !important; letter-spacing: 0.06em;
    margin: 0.7rem 0; text-align: center;
}

/* ── RESPONSE CARD ── */
.vc-card { border-radius: 12px; padding: 1.2rem 1.4rem; margin: 0.7rem 0; }
.vc-card.aria { background: rgba(167,139,250,0.055); border: 1px solid rgba(167,139,250,0.12); border-left: 3px solid #A78BFA; }
.vc-card.rex  { background: rgba(56,189,248,0.055);  border: 1px solid rgba(56,189,248,0.12);  border-left: 3px solid #38BDF8; }
.vc-card.lex  { background: rgba(52,211,153,0.055);  border: 1px solid rgba(52,211,153,0.12);  border-left: 3px solid #34D399; }
.vc-card.max  { background: rgba(251,146,60,0.055);  border: 1px solid rgba(251,146,60,0.12);  border-left: 3px solid #FB923C; }
.vc-card-label { font-family: 'JetBrains Mono', monospace !important; font-size: 0.66rem; font-weight: 500; letter-spacing: 0.1em; margin-bottom: 0.55rem; display: block; }
.vc-card-label.aria { color: #A78BFA !important; }
.vc-card-label.rex  { color: #38BDF8 !important; }
.vc-card-label.lex  { color: #34D399 !important; }
.vc-card-label.max  { color: #FB923C !important; }
.vc-card-text { font-family: 'Barlow', sans-serif !important; font-size: 0.93rem; line-height: 1.75; color: rgba(240,238,248,0.78) !important; }

/* ── VOICE TAG ── */
.vc-vtag {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(52,211,153,0.07); border: 1px solid rgba(52,211,153,0.16);
    color: #34D399 !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem; padding: 3px 10px; border-radius: 3px; letter-spacing: 0.07em;
    margin: 0.65rem 0 0.3rem;
}

/* ── HISTORY ── */
.vc-hist-q {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.055);
    border-radius: 8px; padding: 0.6rem 0.9rem; margin-top: 1.2rem;
    font-family: 'Barlow', sans-serif !important; font-size: 0.85rem;
    color: rgba(240,238,248,0.5) !important; font-style: italic;
}

/* ── COUNCIL ── */
.vc-council-banner {
    background: linear-gradient(135deg, rgba(251,146,60,0.08), rgba(167,139,250,0.08));
    border: 1px solid rgba(251,146,60,0.2);
    border-radius: 10px; padding: 0.9rem 1.2rem; text-align: center;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.72rem;
    color: #FB923C !important; letter-spacing: 0.08em; margin-bottom: 0.8rem;
}

/* ── MIC LABEL ── */
.vc-mic-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: rgba(240,238,248,0.28) !important; margin-bottom: 0.3rem;
}

/* ── FOOTER ── */
.vc-footer { text-align: center; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.04); }
.vc-footer-t { font-family: 'JetBrains Mono', monospace !important; font-size: 0.58rem; color: rgba(255,255,255,0.14) !important; letter-spacing: 0.1em; line-height: 2; }
.vc-footer-t a { color: rgba(167,139,250,0.38) !important; text-decoration: none; margin: 0 0.5rem; }

/* ── TRANSCRIPT BOX ── */
.vc-transcript {
    background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.15);
    border-radius: 8px; padding: 0.65rem 1rem; margin: 0.5rem 0;
    font-family: 'Barlow', sans-serif !important; font-size: 0.85rem;
    color: rgba(240,238,248,0.65) !important;
}
.vc-transcript-label { font-family: 'JetBrains Mono', monospace !important; font-size: 0.6rem; color: #38BDF8 !important; letter-spacing: 0.1em; margin-bottom: 3px; display: block; }

#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = "solo"

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1.2rem;">
    <div class="vc-badge">⚡ ElevenLabs × Groq × AirClaw · Agentic Summer Buildathon</div>
    <div class="vc-title">VocalClaw</div>
    <div class="vc-divider"></div>
    <div class="vc-sub">Voice-In · Voice-Out · Multi-Agent · $0 LLM Cost</div>
    <div class="vc-stats">
        <div><span class="vc-stat-n" style="color:#A78BFA">4</span><span class="vc-stat-l">Agents</span></div>
        <div><span class="vc-stat-n" style="color:#38BDF8">4</span><span class="vc-stat-l">Voices</span></div>
        <div><span class="vc-stat-n" style="color:#34D399">$0</span><span class="vc-stat-l">LLM Cost</span></div>
        <div><span class="vc-stat-n" style="color:#FB923C">∞</span><span class="vc-stat-l">Queries</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── AGENT GRID ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vc-agents">
    <div class="vc-agent">
        <div class="vc-agent-bar" style="background:#A78BFA"></div>
        <span class="vc-agent-icon">🎯</span>
        <span class="vc-agent-name" style="color:#A78BFA">Aria</span>
        <span class="vc-agent-role">Orchestrator</span>
    </div>
    <div class="vc-agent">
        <div class="vc-agent-bar" style="background:#38BDF8"></div>
        <span class="vc-agent-icon">💻</span>
        <span class="vc-agent-name" style="color:#38BDF8">Rex</span>
        <span class="vc-agent-role">Code</span>
    </div>
    <div class="vc-agent">
        <div class="vc-agent-bar" style="background:#34D399"></div>
        <span class="vc-agent-icon">⚖️</span>
        <span class="vc-agent-name" style="color:#34D399">Lex</span>
        <span class="vc-agent-role">Legal</span>
    </div>
    <div class="vc-agent">
        <div class="vc-agent-bar" style="background:#FB923C"></div>
        <span class="vc-agent-icon">🔬</span>
        <span class="vc-agent-name" style="color:#FB923C">Max</span>
        <span class="vc-agent-role">Research</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ──────────────────────────────────────────────────────────────
st.markdown("""<div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; 
letter-spacing:0.12em; text-transform:uppercase; color:rgba(240,238,248,0.25); margin-bottom:0.4rem;">
Mode</div>""", unsafe_allow_html=True)

mc1, mc2 = st.columns(2)
with mc1:
    if st.button("🎯  Solo Mode — One Expert Answers", use_container_width=True):
        st.session_state.mode = "solo"
with mc2:
    if st.button("⚡  Council Mode — All 4 Agents Respond", use_container_width=True):
        st.session_state.mode = "council"

mode_cls = "active-solo" if st.session_state.mode == "solo" else "active-council"
mode_label = "🎯 SOLO MODE — Best agent answers" if st.session_state.mode == "solo" else "⚡ COUNCIL MODE — All 4 agents respond in their own voice"
mode_color = "#A78BFA" if st.session_state.mode == "solo" else "#FB923C"
st.markdown(f"""<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); 
border-radius:8px; padding:0.5rem 1rem; text-align:center; 
font-family:'JetBrains Mono',monospace; font-size:0.68rem; letter-spacing:0.08em; 
color:{mode_color}; margin-bottom:1.2rem;">{mode_label}</div>""", unsafe_allow_html=True)

# ── MIC INPUT ──────────────────────────────────────────────────────────────────
st.markdown('<div class="vc-mic-label">🎤 Voice Input — Record then Ask</div>', unsafe_allow_html=True)
audio_input = st.audio_input("Record your question", label_visibility="collapsed")

transcript = None
if audio_input is not None:
    audio_bytes = audio_input.getvalue()
    with st.spinner("🎤 ElevenLabs Scribe transcribing..."):
        transcript = scribe_stt(audio_bytes)
    if transcript:
        st.markdown(f"""
        <div class="vc-transcript">
            <span class="vc-transcript-label">SCRIBE TRANSCRIPT</span>
            {transcript}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Transcription failed — type your question below instead.")

# ── TEXT INPUT ─────────────────────────────────────────────────────────────────
question_text = st.text_area(
    "q", value=transcript or "",
    placeholder="Or type: 'Explain IPC Section 302'  ·  'Write a Python parser'  ·  'What caused the 2008 crash'",
    height=90, label_visibility="collapsed"
)

# final question = transcript if recorded, else typed
question = question_text.strip()

# ── CONTROLS ───────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 1.2, 0.8])
with c1:
    ask_btn = st.button("⚡  Ask VocalClaw", use_container_width=True)
with c2:
    agent_pick = st.selectbox("Force agent", ["Auto"] + list(AGENTS.keys()), label_visibility="visible")
with c3:
    if st.button("🗑️", use_container_width=True, help="Clear history"):
        st.session_state.history = []
        st.rerun()

# ── PROCESS ────────────────────────────────────────────────────────────────────
if ask_btn and question:
    chosen = agent_pick if agent_pick != "Auto" else detect_agent(question)

    # Build short context from history
    ctx = " | ".join([f"Q: {h['q']} A({h['agent']}): {h['text'][:80]}" for h in st.session_state.history[-3:]])

    if st.session_state.mode == "solo":
        # ── SOLO MODE ──────────────────────────────────────────────────────────
        agent = AGENTS[chosen]
        cls = agent["cls"]

        if agent_pick == "Auto":
            st.markdown(f"""<div class="vc-routing">🧠 Aria routing → 
            <strong style="color:{agent['color']}">{agent['emoji']} {chosen}</strong> · {agent['role']}</div>""",
            unsafe_allow_html=True)

            # Aria speaks the handoff
            handoff_line = f"Routing your question to {chosen}, our {agent['role']}."
            with st.spinner("Aria announcing handoff..."):
                handoff_audio = tts(handoff_line, AGENTS["Aria"]["voice_id"])
            if handoff_audio:
                st.audio(handoff_audio, format="audio/mpeg")

        with st.spinner(f"{chosen} thinking..."):
            text = groq(chosen, question, ctx)

        if text:
            st.markdown(f"""
            <div class="vc-card {cls}">
                <span class="vc-card-label {cls}">{agent['emoji']} {chosen.upper()} — {agent['role'].upper()}</span>
                <div class="vc-card-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner(f"ElevenLabs generating {chosen}'s voice..."):
                audio = tts(text, agent["voice_id"])
            if audio:
                st.markdown(f'<div class="vc-vtag">🔊 Speaking as {chosen} via ElevenLabs</div>', unsafe_allow_html=True)
                st.audio(audio, format="audio/mpeg")

            st.session_state.history.append({"q": question, "agent": chosen, "text": text})
        else:
            st.error("Groq API failed — check API key or try again.")

    else:
        # ── COUNCIL MODE ───────────────────────────────────────────────────────
        st.markdown("""
        <div class="vc-council-banner">
            ⚡ COUNCIL MODE — All 4 agents will respond in their own voice
        </div>
        """, unsafe_allow_html=True)

        # Aria opens the council
        intro = f"The council is now in session. All four agents will weigh in on: {question}"
        with st.spinner("Aria opening the council..."):
            intro_audio = tts(intro, AGENTS["Aria"]["voice_id"])
        if intro_audio:
            st.audio(intro_audio, format="audio/mpeg")

        council_responses = []
        for name, agent in AGENTS.items():
            cls = agent["cls"]
            council_prompt = f"From your perspective as {agent['role']}, answer this briefly in 2-3 sentences: {question}"

            with st.spinner(f"{name} ({agent['role']}) responding..."):
                text = groq(name, council_prompt, ctx)

            if text:
                st.markdown(f"""
                <div class="vc-card {cls}">
                    <span class="vc-card-label {cls}">{agent['emoji']} {name.upper()} — {agent['role'].upper()}</span>
                    <div class="vc-card-text">{text}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner(f"ElevenLabs: {name}'s voice..."):
                    audio = tts(text, agent["voice_id"])
                if audio:
                    st.markdown(f'<div class="vc-vtag">🔊 {name} · ElevenLabs</div>', unsafe_allow_html=True)
                    st.audio(audio, format="audio/mpeg")

                council_responses.append(f"{name}: {text}")

        # Aria synthesizes
        if council_responses:
            synth_prompt = f"In 2 sentences, synthesize the council's different perspectives into one final insight: {' | '.join(council_responses)}"
            with st.spinner("Aria synthesizing the council..."):
                synth = groq("Aria", synth_prompt)
            if synth:
                st.markdown(f"""
                <div class="vc-card aria" style="margin-top:1rem; border:1px solid rgba(167,139,250,0.25);">
                    <span class="vc-card-label aria">🎯 ARIA — COUNCIL SYNTHESIS</span>
                    <div class="vc-card-text">{synth}</div>
                </div>
                """, unsafe_allow_html=True)
                with st.spinner("Aria's final voice..."):
                    synth_audio = tts(synth, AGENTS["Aria"]["voice_id"])
                if synth_audio:
                    st.markdown('<div class="vc-vtag">🔊 Aria Synthesis · ElevenLabs</div>', unsafe_allow_html=True)
                    st.audio(synth_audio, format="audio/mpeg")

            st.session_state.history.append({"q": question, "agent": "Council", "text": " | ".join(council_responses)})

elif ask_btn:
    st.warning("Record or type a question first!")

# ── HISTORY ────────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("""<div style="margin-top:2rem; font-family:'JetBrains Mono',monospace; 
    font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; 
    color:rgba(240,238,248,0.2); margin-bottom:0.5rem;">Session History</div>""", unsafe_allow_html=True)

    for item in reversed(st.session_state.history[-5:]):
        agent_color = AGENTS.get(item["agent"], {}).get("color", "#888") if item["agent"] != "Council" else "#FB923C"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.015); border:1px solid rgba(255,255,255,0.05); 
        border-radius:8px; padding:0.6rem 0.9rem; margin-bottom:0.4rem;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; 
            color:{agent_color}; letter-spacing:0.1em;">{item['agent'].upper()}</span>
            <span style="font-family:'Barlow',sans-serif; font-size:0.82rem; 
            color:rgba(240,238,248,0.38); margin-left:0.5rem; font-style:italic;">"{item['q']}"</span>
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vc-footer">
    <div class="vc-footer-t">
        ELEVENLABS VOICE + SCRIBE · GROQ INFERENCE · AIRCLAW LOCAL · AGENTIC SUMMER BUILDATHON
        <br>
        <a href="https://github.com/nickzsche21/VocalClaw_11Labs">GitHub ↗</a>
        <a href="https://elevenlabs.io">ElevenLabs ↗</a>
        <a href="https://groq.com">Groq ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)
