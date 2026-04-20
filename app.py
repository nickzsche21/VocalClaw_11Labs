import streamlit as st
import requests
import base64
import os

# ── KEYS — reads from Streamlit Secrets OR env vars ───────────────────────────
EL_KEY   = st.secrets.get("ELEVENLABS_API_KEY", os.environ.get("ELEVENLABS_API_KEY", "sk_cabe7e77c8067fac91d6fde4bbc461b894f617353fc932a3"))
GROQ_KEY = st.secrets.get("GROQ_API_KEY",       os.environ.get("GROQ_API_KEY",       "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"))

# ── AGENTS ────────────────────────────────────────────────────────────────────
AGENTS = {
    "Aria": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "color": "#C4B5FD", "cls": "aria", "emoji": "🎯",
        "role": "Orchestrator",
        "system": "You are Aria, an intelligent AI orchestrator. Warm, sharp, authoritative. 2-3 sentences max. When routing, naturally mention you're handing off.",
        "keywords": []
    },
    "Rex": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "color": "#7DD3FC", "cls": "rex", "emoji": "💻",
        "role": "Code Specialist",
        "system": "You are Rex, an elite software engineer. Direct, precise, technical. Include concise code when relevant. 3-4 sentences max.",
        "keywords": ["code","python","javascript","function","bug","error","debug","program","script","api","database","algorithm","syntax","class","loop","array","compile","runtime","git","deploy","react","css","html","typescript","sql","bash"]
    },
    "Lex": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "color": "#6EE7B7", "cls": "lex", "emoji": "⚖️",
        "role": "Legal Specialist",
        "system": "You are Lex, a brilliant Indian legal specialist. Authoritative, precise, cite IPC/CrPC/Constitution when relevant. 3-4 sentences max.",
        "keywords": ["law","legal","ipc","section","court","statute","act","rights","contract","criminal","civil","judge","advocate","petition","bail","verdict","constitution","crpc","fir","arrest","offence","punishment","lawyer","case","judgment","article"]
    },
    "Max": {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "color": "#FCA5A5", "cls": "max", "emoji": "🔬",
        "role": "Research Specialist",
        "system": "You are Max, a deep research specialist. Synthesize complex topics into sharp, fascinating insights. Science, history, economics, tech. 3-4 sentences max.",
        "keywords": ["research","explain","what is","how does","why","history","science","data","compare","difference","study","facts","tell me","who is","when did","where is","economics","politics","medicine","physics","biology","what happened"]
    }
}

GROQ_MODELS = ["llama-3.1-8b-instant","llama3-8b-8192","mixtral-8x7b-32768","gemma-7b-it"]

# ── AUDIO QUEUE (plays sequentially, not overlapping) ─────────────────────────
AUDIO_QUEUE_JS = """
<script>
window._vc_queue = window._vc_queue || [];
window._vc_playing = window._vc_playing || false;

function vcEnqueue(b64, label) {
    window._vc_queue.push({b64, label});
    if (!window._vc_playing) vcPlayNext();
}

function vcPlayNext() {
    if (window._vc_queue.length === 0) {
        window._vc_playing = false;
        return;
    }
    window._vc_playing = true;
    const item = window._vc_queue.shift();
    const audio = new Audio('data:audio/mpeg;base64,' + item.b64);
    audio.onended = vcPlayNext;
    audio.onerror = vcPlayNext;
    audio.play().catch(vcPlayNext);
}
</script>
"""

_queue_init = False

def init_queue():
    global _queue_init
    if not _queue_init:
        st.markdown(AUDIO_QUEUE_JS, unsafe_allow_html=True)
        _queue_init = True

def play_audio(audio_bytes, label=""):
    """Queue audio to play sequentially."""
    if not audio_bytes:
        return
    b64 = base64.b64encode(audio_bytes).decode()
    if label:
        st.markdown(f'<div class="vc-vtag">🔊 {label}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <script>vcEnqueue("{b64}", "{label}");</script>
    """, unsafe_allow_html=True)

# ── API HELPERS ───────────────────────────────────────────────────────────────
def groq(agent_name, question, context=""):
    system = AGENTS[agent_name]["system"]
    if context:
        system += f"\n\nPrior context: {context}"
    for model in GROQ_MODELS:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": model,
                      "messages": [{"role":"system","content":system},{"role":"user","content":question}],
                      "max_tokens": 180, "temperature": 0.75},
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

def scribe(audio_bytes):
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

def detect(text):
    t = text.lower()
    for name, info in AGENTS.items():
        if name == "Aria": continue
        if any(w in t for w in info["keywords"]):
            return name
    return "Aria"

# ── PAGE ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="VocalClaw", page_icon="🎙️", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp { background: #080810 !important; }
.block-container { max-width: 720px !important; padding: 0 1.5rem 5rem !important; }

/* ── HERO ── */
.vc-hero { text-align: center; padding: 3.5rem 0 2.5rem; }

.vc-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(196,181,253,0.07); border: 1px solid rgba(196,181,253,0.18);
    color: #C4B5FD !important; font-family: 'JetBrains Mono',monospace !important;
    font-size: 0.58rem; letter-spacing: 0.2em; padding: 5px 14px;
    border-radius: 2px; text-transform: uppercase; margin-bottom: 1.4rem;
}

.vc-wordmark {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: clamp(4.5rem, 13vw, 7rem);
    letter-spacing: 0.08em; line-height: 0.88;
    background: linear-gradient(165deg, #ffffff 25%, #C4B5FD 58%, #7DD3FC 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.5rem;
}

.vc-rule { width: 32px; height: 1px; background: rgba(196,181,253,0.28); margin: 1rem auto; }

.vc-descriptor {
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.6rem;
    letter-spacing: 0.2em; color: rgba(255,255,255,0.2) !important;
    text-transform: uppercase; margin-bottom: 2.5rem;
}

/* ── STATS ── */
.vc-stats { display: flex; justify-content: center; align-items: flex-start; gap: 3rem; margin-bottom: 3rem; }
.vc-s-num { font-family: 'Bebas Neue',sans-serif !important; font-size: 2.6rem; letter-spacing: 0.04em; display: block; line-height: 1; }
.vc-s-lbl { font-family: 'JetBrains Mono',monospace !important; font-size: 0.52rem; letter-spacing: 0.16em; color: rgba(255,255,255,0.2) !important; text-transform: uppercase; display: block; margin-top: 3px; }

/* ── AGENT TILES ── */
.vc-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 2rem; }
.vc-tile {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px; padding: 1rem 0.5rem 0.85rem; text-align: center; position: relative;
}
.vc-tile-accent { position: absolute; top:0; left:20%; right:20%; height:1px; }
.vc-tile-icon { font-size: 1.3rem; display: block; margin-bottom: 0.3rem; }
.vc-tile-name { font-family: 'Inter',sans-serif !important; font-weight: 600; font-size: 0.85rem; display: block; }
.vc-tile-role { font-family: 'JetBrains Mono',monospace !important; font-size: 0.5rem; color: rgba(255,255,255,0.2) !important; letter-spacing: 0.12em; text-transform: uppercase; display: block; margin-top: 2px; }

/* ── SECTION LABEL ── */
.vc-label {
    font-family: 'JetBrains Mono',monospace !important; font-size: 0.58rem;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: rgba(255,255,255,0.2) !important; margin-bottom: 0.5rem; display: block;
}

/* ── MODE BUTTONS ── */
.stButton > button {
    background: rgba(255,255,255,0.03) !important; color: rgba(255,255,255,0.5) !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 6px !important;
    font-family: 'Inter',sans-serif !important; font-weight: 500 !important;
    font-size: 0.8rem !important; padding: 0.55rem 1rem !important;
    transition: all 0.15s ease !important; letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: rgba(196,181,253,0.08) !important;
    border-color: rgba(196,181,253,0.25) !important;
    color: #C4B5FD !important;
}

/* ── ACTIVE MODE BADGE ── */
.vc-mode-active {
    border-radius: 6px; padding: 0.55rem 1rem; text-align: center;
    font-family: 'JetBrains Mono',monospace !important; font-size: 0.65rem;
    letter-spacing: 0.1em; margin-bottom: 1.4rem; border: 1px solid;
}

/* ── TEXT AREA ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.025) !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important; color: #F0EEF8 !important;
    font-family: 'Inter',sans-serif !important; font-size: 0.92rem !important;
    padding: 0.9rem !important; line-height: 1.65 !important; resize: none !important;
}
.stTextArea textarea:focus { border-color: rgba(196,181,253,0.35) !important; outline: none !important; box-shadow: none !important; }
.stTextArea textarea::placeholder { color: rgba(255,255,255,0.15) !important; }
.stTextArea label { display:none !important; }

/* ── ASK BUTTON ── */
button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #5B21B6, #3730A3) !important;
    color: #fff !important; border: none !important; border-radius: 7px !important;
    font-family: 'Inter',sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; padding: 0.62rem 1.4rem !important;
    box-shadow: 0 0 0 1px rgba(91,33,182,0.4), 0 4px 20px rgba(91,33,182,0.25) !important;
}

/* ── SELECT ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.025) !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 7px !important; color: rgba(255,255,255,0.65) !important;
    font-family: 'Inter',sans-serif !important; font-size: 0.85rem !important;
}
.stSelectbox svg { fill: rgba(255,255,255,0.25) !important; }
.stSelectbox label { color: rgba(255,255,255,0.2) !important; font-family: 'JetBrains Mono',monospace !important; font-size: 0.58rem !important; letter-spacing: 0.16em; text-transform: uppercase; }

/* ── ROUTING ── */
.vc-route {
    background: rgba(196,181,253,0.05); border: 1px solid rgba(196,181,253,0.12);
    border-radius: 7px; padding: 0.6rem 1rem; margin: 0.7rem 0;
    font-family: 'JetBrains Mono',monospace !important; font-size: 0.68rem;
    color: rgba(255,255,255,0.38) !important; letter-spacing: 0.07em; text-align: center;
}

/* ── RESPONSE CARD ── */
.vc-card { border-radius: 10px; padding: 1.2rem 1.35rem; margin: 0.6rem 0; position: relative; overflow: hidden; }
.vc-card::before { content:''; position:absolute; top:0; left:0; width:2px; height:100%; }
.vc-card.aria { background:rgba(196,181,253,0.045); border:1px solid rgba(196,181,253,0.1); }
.vc-card.aria::before { background:#C4B5FD; }
.vc-card.rex  { background:rgba(125,211,252,0.045); border:1px solid rgba(125,211,252,0.1); }
.vc-card.rex::before  { background:#7DD3FC; }
.vc-card.lex  { background:rgba(110,231,183,0.045); border:1px solid rgba(110,231,183,0.1); }
.vc-card.lex::before  { background:#6EE7B7; }
.vc-card.max  { background:rgba(252,165,165,0.045); border:1px solid rgba(252,165,165,0.1); }
.vc-card.max::before  { background:#FCA5A5; }

.vc-card-hd { font-family:'JetBrains Mono',monospace !important; font-size:0.62rem; font-weight:500; letter-spacing:0.12em; margin-bottom:0.55rem; display:block; }
.vc-card-hd.aria { color:#C4B5FD !important; }
.vc-card-hd.rex  { color:#7DD3FC !important; }
.vc-card-hd.lex  { color:#6EE7B7 !important; }
.vc-card-hd.max  { color:#FCA5A5 !important; }
.vc-card-body { font-family:'Inter',sans-serif !important; font-size:0.92rem; line-height:1.75; color:rgba(240,238,248,0.78) !important; }

/* ── VOICE TAG ── */
.vc-vtag {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(110,231,183,0.06); border: 1px solid rgba(110,231,183,0.15);
    color: #6EE7B7 !important; font-family: 'JetBrains Mono',monospace !important;
    font-size: 0.58rem; padding: 3px 10px; border-radius: 3px; letter-spacing: 0.08em;
    margin: 0.6rem 0 0.25rem;
}

/* ── TRANSCRIPT ── */
.vc-tx {
    background: rgba(125,211,252,0.05); border: 1px solid rgba(125,211,252,0.12);
    border-radius: 7px; padding: 0.65rem 0.9rem; margin: 0.5rem 0;
    font-family:'Inter',sans-serif !important; font-size:0.88rem;
    color:rgba(240,238,248,0.55) !important; font-style:italic;
}
.vc-tx-lbl { font-family:'JetBrains Mono',monospace !important; font-size:0.56rem; color:#7DD3FC !important; letter-spacing:0.1em; margin-bottom:3px; display:block; }

/* ── COUNCIL BANNER ── */
.vc-council {
    background: linear-gradient(135deg, rgba(252,165,165,0.06), rgba(196,181,253,0.06));
    border: 1px solid rgba(252,165,165,0.15); border-radius: 8px;
    padding: 0.85rem 1.1rem; text-align: center;
    font-family:'JetBrains Mono',monospace !important; font-size:0.68rem;
    color:#FCA5A5 !important; letter-spacing:0.1em; margin-bottom:0.8rem;
}

/* ── HISTORY ── */
.vc-hist-item {
    background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.045);
    border-radius: 7px; padding: 0.55rem 0.85rem; margin-bottom: 0.35rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.vc-hist-agent { font-family:'JetBrains Mono',monospace !important; font-size:0.56rem; letter-spacing:0.1em; min-width:60px; }
.vc-hist-q { font-family:'Inter',sans-serif !important; font-size:0.8rem; color:rgba(240,238,248,0.32) !important; font-style:italic; }

/* ── FOOTER ── */
.vc-footer { text-align:center; margin-top:3.5rem; padding-top:1.5rem; border-top:1px solid rgba(255,255,255,0.04); }
.vc-footer-t { font-family:'JetBrains Mono',monospace !important; font-size:0.56rem; color:rgba(255,255,255,0.13) !important; letter-spacing:0.12em; line-height:2.2; }
.vc-footer-t a { color:rgba(196,181,253,0.35) !important; text-decoration:none; margin:0 0.5rem; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header, .stDeployButton { display:none !important; }

/* ── MIC LABEL ── */
.vc-mic { font-family:'JetBrains Mono',monospace !important; font-size:0.58rem; letter-spacing:0.18em; text-transform:uppercase; color:rgba(255,255,255,0.18) !important; margin-bottom:0.4rem; display:block; }
</style>
""", unsafe_allow_html=True)

# Init audio queue JS
init_queue()

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "history" not in st.session_state: st.session_state.history = []
if "mode"    not in st.session_state: st.session_state.mode = "solo"

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vc-hero">
    <div class="vc-pill">⚡ ElevenLabs × Groq × AirClaw &nbsp;·&nbsp; Agentic Summer Buildathon</div>
    <div class="vc-wordmark">VocalClaw</div>
    <div class="vc-rule"></div>
    <div class="vc-descriptor">Voice-In · Voice-Out · Multi-Agent · $0 LLM Cost</div>
    <div class="vc-stats">
        <div><span class="vc-s-num" style="color:#C4B5FD">4</span><span class="vc-s-lbl">Agents</span></div>
        <div><span class="vc-s-num" style="color:#7DD3FC">4</span><span class="vc-s-lbl">Voices</span></div>
        <div><span class="vc-s-num" style="color:#6EE7B7">$0</span><span class="vc-s-lbl">LLM Cost</span></div>
        <div><span class="vc-s-num" style="color:#FCA5A5">∞</span><span class="vc-s-lbl">Queries</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── AGENT GRID ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vc-grid">
    <div class="vc-tile"><div class="vc-tile-accent" style="background:#C4B5FD"></div><span class="vc-tile-icon">🎯</span><span class="vc-tile-name" style="color:#C4B5FD">Aria</span><span class="vc-tile-role">Orchestrator</span></div>
    <div class="vc-tile"><div class="vc-tile-accent" style="background:#7DD3FC"></div><span class="vc-tile-icon">💻</span><span class="vc-tile-name" style="color:#7DD3FC">Rex</span><span class="vc-tile-role">Code</span></div>
    <div class="vc-tile"><div class="vc-tile-accent" style="background:#6EE7B7"></div><span class="vc-tile-icon">⚖️</span><span class="vc-tile-name" style="color:#6EE7B7">Lex</span><span class="vc-tile-role">Legal</span></div>
    <div class="vc-tile"><div class="vc-tile-accent" style="background:#FCA5A5"></div><span class="vc-tile-icon">🔬</span><span class="vc-tile-name" style="color:#FCA5A5">Max</span><span class="vc-tile-role">Research</span></div>
</div>
""", unsafe_allow_html=True)

# ── MODE ───────────────────────────────────────────────────────────────────────
st.markdown('<span class="vc-label">Mode</span>', unsafe_allow_html=True)
mc1, mc2 = st.columns(2)
with mc1:
    if st.button("🎯  Solo — One Expert Answers", use_container_width=True):
        st.session_state.mode = "solo"
with mc2:
    if st.button("⚡  Council — All 4 Voices Debate", use_container_width=True):
        st.session_state.mode = "council"

if st.session_state.mode == "solo":
    st.markdown("""<div class="vc-mode-active" style="background:rgba(196,181,253,0.06);border-color:rgba(196,181,253,0.2);color:#C4B5FD;">
    🎯 SOLO MODE — Best agent answers in their voice</div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="vc-mode-active" style="background:rgba(252,165,165,0.06);border-color:rgba(252,165,165,0.2);color:#FCA5A5;">
    ⚡ COUNCIL MODE — All 4 agents respond sequentially in their own voice</div>""", unsafe_allow_html=True)

# ── MIC ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="vc-mic">🎤 Voice Input</span>', unsafe_allow_html=True)
audio_in = st.audio_input("mic", label_visibility="collapsed")

transcript = None
if audio_in:
    with st.spinner("Scribe transcribing..."):
        transcript = scribe(audio_in.getvalue())
    if transcript:
        st.markdown(f'<div class="vc-tx"><span class="vc-tx-lbl">SCRIBE TRANSCRIPT</span>{transcript}</div>', unsafe_allow_html=True)
    else:
        st.caption("Transcription failed — type below instead.")

# ── TEXT INPUT ─────────────────────────────────────────────────────────────────
question = st.text_area("q", value=transcript or "",
    placeholder="Try: 'Explain IPC Section 302'  ·  'Write a Python scraper'  ·  'What caused the 2008 crash'",
    height=95, label_visibility="collapsed")

c1, c2, c3 = st.columns([3, 1.2, 0.7])
with c1: ask = st.button("⚡  Ask VocalClaw", use_container_width=True, type="primary")
with c2: agent_pick = st.selectbox("Agent", ["Auto"]+list(AGENTS.keys()))
with c3:
    if st.button("🗑️", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ── PROCESS ────────────────────────────────────────────────────────────────────
q = question.strip()

if ask and q:
    chosen = agent_pick if agent_pick != "Auto" else detect(q)
    ctx = " | ".join([f"{h['agent']}: {h['text'][:70]}" for h in st.session_state.history[-3:]])

    if st.session_state.mode == "solo":
        agent = AGENTS[chosen]
        cls   = agent["cls"]

        # Aria announces handoff (if auto-routed to specialist)
        if agent_pick == "Auto" and chosen != "Aria":
            st.markdown(f'<div class="vc-route">🧠 Aria → <strong style="color:{agent["color"]}">{agent["emoji"]} {chosen}</strong> · {agent["role"]}</div>', unsafe_allow_html=True)
            handoff = f"Routing you to {chosen}, our {agent['role']}."
            with st.spinner("Aria announcing..."):
                ha = tts(handoff, AGENTS["Aria"]["voice_id"])
            play_audio(ha, f"Aria → {chosen}")

        with st.spinner(f"{chosen} thinking..."):
            text = groq(chosen, q, ctx)

        if text:
            st.markdown(f"""
            <div class="vc-card {cls}">
                <span class="vc-card-hd {cls}">{agent['emoji']} {chosen.upper()} — {agent['role'].upper()}</span>
                <div class="vc-card-body">{text}</div>
            </div>""", unsafe_allow_html=True)
            with st.spinner(f"ElevenLabs: {chosen}'s voice..."):
                audio = tts(text, agent["voice_id"])
            play_audio(audio, f"Speaking as {chosen}")
            st.session_state.history.append({"q": q, "agent": chosen, "text": text})
        else:
            st.error("Groq API failed — all models unavailable.")

    else:
        # ── COUNCIL MODE — sequential audio queue ──────────────────────────────
        st.markdown('<div class="vc-council">⚡ COUNCIL IN SESSION — voices will play one after another</div>', unsafe_allow_html=True)

        # Aria opens
        intro = f"The council is now in session. All four agents will share their perspective on: {q}"
        with st.spinner("Aria opening council..."):
            ia = tts(intro, AGENTS["Aria"]["voice_id"])
        play_audio(ia, "Aria — Council Open")

        council_texts = []
        for name, agent in AGENTS.items():
            prompt = f"From your perspective as {agent['role']}, give a sharp 2-sentence take on: {q}"
            with st.spinner(f"{name} responding..."):
                text = groq(name, prompt, ctx)
            if text:
                st.markdown(f"""
                <div class="vc-card {agent['cls']}">
                    <span class="vc-card-hd {agent['cls']}">{agent['emoji']} {name.upper()}</span>
                    <div class="vc-card-body">{text}</div>
                </div>""", unsafe_allow_html=True)
                with st.spinner(f"ElevenLabs: {name}..."):
                    audio = tts(text, agent["voice_id"])
                play_audio(audio, name)
                council_texts.append(f"{name}: {text}")

        # Aria synthesizes
        if council_texts:
            syn_q = f"In 2 sentences, give one final synthesized insight from all perspectives: {' | '.join(council_texts)}"
            with st.spinner("Aria synthesizing..."):
                syn = groq("Aria", syn_q)
            if syn:
                st.markdown(f"""
                <div class="vc-card aria" style="border-color:rgba(196,181,253,0.22) !important;">
                    <span class="vc-card-hd aria">🎯 ARIA — SYNTHESIS</span>
                    <div class="vc-card-body">{syn}</div>
                </div>""", unsafe_allow_html=True)
                with st.spinner("Aria final voice..."):
                    syn_a = tts(syn, AGENTS["Aria"]["voice_id"])
                play_audio(syn_a, "Aria Synthesis")
            st.session_state.history.append({"q": q, "agent": "Council", "text": " | ".join(council_texts)})

elif ask:
    st.warning("Record or type a question first!")

# ── HISTORY ────────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<span class="vc-label" style="margin-top:2rem;display:block">Session History</span>', unsafe_allow_html=True)
    for item in reversed(st.session_state.history[-5:]):
        color = AGENTS.get(item["agent"], {}).get("color","#888") if item["agent"] != "Council" else "#FCA5A5"
        st.markdown(f"""
        <div class="vc-hist-item">
            <span class="vc-hist-agent" style="color:{color}">{item['agent'].upper()}</span>
            <span class="vc-hist-q">"{item['q']}"</span>
        </div>""", unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vc-footer"><div class="vc-footer-t">
    ELEVENLABS SCRIBE + TTS &nbsp;·&nbsp; GROQ LLAMA3 &nbsp;·&nbsp; AGENTIC SUMMER BUILDATHON
    <br>
    <a href="https://github.com/nickzsche21/VocalClaw_11Labs">GitHub ↗</a>
    <a href="https://elevenlabs.io">ElevenLabs ↗</a>
    <a href="https://groq.com">Groq ↗</a>
    <a href="https://jurixoneai.com">JurixAI ↗</a>
</div></div>
""", unsafe_allow_html=True)
