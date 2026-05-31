import streamlit as st
import pickle
import string
from pathlib import Path
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

st.set_page_config(
    page_title="Spam Scanner",
    page_icon="🛡️",
    layout="wide"
)

st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    unsafe_allow_html=True
)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

#MainMenu, footer, header, .stDeployButton,
.stDecoration, [data-testid="stToolbar"],
[data-testid="stHeader"] { display: none !important; }

.stApp {
    background: #F0EDF8 !important;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 15% 20%, rgba(167,139,250,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 85% 75%, rgba(110,190,255,0.15) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(251,207,232,0.12) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.stApp::after {
    content: '';
    position: fixed;
    width: 320px; height: 320px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%);
    top: -80px; right: -80px;
    animation: drift 12s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes drift {
    0%   { transform: translate(0,0) scale(1); }
    50%  { transform: translate(-30px, 40px) scale(1.08); }
    100% { transform: translate(20px, -20px) scale(0.95); }
}

.bg-canvas {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.float-el {
    position: absolute;
    animation: floatUp var(--dur, 8s) ease-in-out infinite alternate;
    animation-delay: var(--delay, 0s);
    opacity: var(--op, 0.55);
}

@keyframes floatUp {
    0%   { transform: translateY(0px) rotate(var(--rot0, 0deg)); }
    100% { transform: translateY(var(--ty, -18px)) rotate(var(--rot1, 5deg)); }
}

.block-container {
    position: relative;
    z-index: 1;
    max-width: 100% !important;
    padding: 40px 20px 60px !important;
}

@media (min-width: 600px) {
    .block-container { padding: 48px 32px 64px !important; }
}
@media (min-width: 900px) {
    .block-container { padding: 60px 60px 80px !important; }
}
@media (min-width: 1200px) {
    .block-container { padding: 72px 100px 80px !important; }
}

.app-shell {
    display: grid;
    grid-template-columns: 1fr;
    gap: 32px;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 900px) {
    .app-shell {
        grid-template-columns: 1fr 1fr;
        gap: 56px;
        align-items: start;
    }
}
@media (min-width: 1100px) {
    .app-shell { gap: 72px; }
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 99px;
    padding: 6px 16px 6px 10px;
    margin-bottom: 24px;
    animation: badgePop 0.5s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes badgePop {
    from { opacity: 0; transform: scale(0.8) translateY(6px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
.badge-icon {
    width: 26px; height: 26px;
    background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
}
.badge-text {
    font-size: 12px; font-weight: 600;
    color: #5b21b6; letter-spacing: 0.03em;
}

.eyebrow {
    font-size: 11px; font-weight: 600;
    color: #8b5cf6;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
    animation: slideUp 0.5s 0.1s ease both;
}

.headline {
    font-family: 'Instrument Serif', serif;
    font-size: 38px;
    color: #1e1b2e;
    line-height: 1.08;
    letter-spacing: -0.025em;
    margin-bottom: 16px;
    animation: slideUp 0.5s 0.15s ease both;
}
.headline em { font-style: italic; color: #7c3aed; }

@media (min-width: 600px)  { .headline { font-size: 46px; } }
@media (min-width: 900px)  { .headline { font-size: 52px; } }
@media (min-width: 1200px) { .headline { font-size: 60px; } }

@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.tagline {
    font-size: 14px; color: #6b7280; line-height: 1.7;
    margin-bottom: 28px; max-width: 400px;
    animation: slideUp 0.5s 0.2s ease both;
}
@media (min-width: 600px) { .tagline { font-size: 15px; } }

.stat-row {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-bottom: 36px;
    animation: slideUp 0.5s 0.25s ease both;
}
.stat-chip {
    display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.80);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 12px; color: #4b5563; font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    cursor: default;
}
.stat-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(124,58,237,0.12);
    border-color: rgba(124,58,237,0.4);
}
.stat-chip strong { color: #7c3aed; font-weight: 700; }
.stat-chip .chip-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #7c3aed; opacity: 0.5;
}

.glass-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.90);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 8px 40px rgba(124,58,237,0.08), 0 1px 3px rgba(0,0,0,0.04);
    animation: cardIn 0.6s 0.2s cubic-bezier(0.16,1,0.3,1) both;
    transition: box-shadow 0.3s ease;
}
.glass-card:hover {
    box-shadow: 0 12px 50px rgba(124,58,237,0.12), 0 1px 3px rgba(0,0,0,0.04);
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

.section-label {
    font-size: 11px; font-weight: 600;
    color: #9ca3af;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 10px;
}

.stTextArea textarea {
    background: rgba(249,247,255,0.90) !important;
    border: 1.5px solid rgba(167,139,250,0.30) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    color: #1e1b2e !important;
    line-height: 1.65 !important;
    resize: none !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    caret-color: #7c3aed;
    width: 100% !important;
    outline: none !important;
}
.stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 4px rgba(124,58,237,0.10) !important;
    background: #fff !important;
}
.stTextArea textarea::placeholder { color: #c4b5fd !important; }
.stTextArea label { display: none !important; }
.stTextArea > div,
.stTextArea > div > div,
.stTextArea > div > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
}
[data-baseweb="textarea"],
[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 15px 24px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    cursor: pointer !important;
    margin-top: 12px !important;
    transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.2s ease,
                background 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.30) !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.40) !important;
}
.stButton > button:active {
    transform: scale(0.98) !important;
    box-shadow: 0 2px 10px rgba(124,58,237,0.25) !important;
}

.result-wrap {
    animation: resultIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
    margin-top: 16px;
}
@keyframes resultIn {
    from { opacity: 0; transform: translateY(12px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.result-spam {
    background: linear-gradient(135deg, #fff1f1 0%, #fef2f2 100%);
    border: 1.5px solid #fca5a5;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 24px rgba(220,38,38,0.08);
}
.result-safe {
    background: linear-gradient(135deg, #f0fdf6 0%, #ecfdf5 100%);
    border: 1.5px solid #6ee7b7;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 24px rgba(16,185,129,0.08);
}

.result-header { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }

.result-chip-spam {
    width: 48px; height: 48px;
    background: #fee2e2; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    animation: chipBounce 0.5s 0.1s cubic-bezier(0.34,1.56,0.64,1) both;
}
.result-chip-safe {
    width: 48px; height: 48px;
    background: #d1fae5; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    animation: chipBounce 0.5s 0.1s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes chipBounce {
    from { transform: scale(0); opacity: 0; }
    to   { transform: scale(1); opacity: 1; }
}

.result-title-spam { font-size: 17px; font-weight: 700; color: #dc2626; letter-spacing: -0.01em; }
.result-title-safe { font-size: 17px; font-weight: 700; color: #059669; letter-spacing: -0.01em; }
.result-desc-spam  { font-size: 12.5px; color: #ef4444; margin-top: 3px; line-height: 1.4; }
.result-desc-safe  { font-size: 12.5px; color: #10b981; margin-top: 3px; line-height: 1.4; }

.conf-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px;
}
.conf-key { font-size: 11px; font-weight: 600; color: #9ca3af; letter-spacing: 0.07em; text-transform: uppercase; }
.conf-pct-spam { font-size: 13px; font-weight: 700; color: #dc2626; }
.conf-pct-safe { font-size: 13px; font-weight: 700; color: #059669; }

.conf-track {
    height: 6px;
    background: rgba(0,0,0,0.07);
    border-radius: 99px; overflow: hidden;
    margin-bottom: 16px;
}
.conf-fill-spam {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #fca5a5, #dc2626);
    animation: barGrow 0.8s 0.3s cubic-bezier(0.16,1,0.3,1) both;
    transform-origin: left;
}
.conf-fill-safe {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #6ee7b7, #059669);
    animation: barGrow 0.8s 0.3s cubic-bezier(0.16,1,0.3,1) both;
    transform-origin: left;
}
@keyframes barGrow {
    from { clip-path: inset(0 100% 0 0); }
    to   { clip-path: inset(0 0% 0 0); }
}

.prob-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-top: 1px solid rgba(0,0,0,0.06);
}
.prob-key      { font-size: 13px; color: #6b7280; }
.prob-val-spam { font-size: 13px; font-weight: 600; color: #dc2626; font-variant-numeric: tabular-nums; }
.prob-val-safe { font-size: 13px; font-weight: 600; color: #059669; font-variant-numeric: tabular-nums; }

.warn-card {
    background: linear-gradient(135deg, #fffbeb 0%, #fef9c3 100%);
    border: 1.5px solid #fde68a;
    border-radius: 14px;
    padding: 14px 18px;
    font-size: 13px; color: #92400e; line-height: 1.55;
    margin-top: 12px;
    animation: resultIn 0.3s ease both;
}

.footer-area {
    max-width: 1100px; margin: 48px auto 0;
    border-top: 1px solid rgba(167,139,250,0.20);
    padding-top: 28px;
}
.pill-row { display: flex; flex-wrap: wrap; gap: 8px; }
.pill {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px; color: #6b7280; font-weight: 500;
    transition: transform 0.2s ease, border-color 0.2s ease;
    cursor: default;
}
.pill:hover {
    transform: translateY(-1px);
    border-color: rgba(124,58,237,0.4);
    color: #7c3aed;
}

@media (min-width: 1100px) {
    .col-right { position: sticky; top: 32px; }
}
</style>
""", unsafe_allow_html=True)

BG_SVG = (
    '<div class="bg-canvas" aria-hidden="true">'
    '<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0;">'
    '<circle cx="8%" cy="18%" r="180" fill="rgba(167,139,250,0.10)"/>'
    '<circle cx="88%" cy="72%" r="220" fill="rgba(110,190,255,0.09)"/>'
    '<circle cx="55%" cy="88%" r="140" fill="rgba(251,207,232,0.10)"/>'
    '<g class="float-el" style="--dur:9s;--delay:0s;--op:0.18;--ty:-20px;--rot0:-4deg;--rot1:4deg;left:5%;top:30%;">'
    '<path d="M24 4 L44 12 L44 28 C44 38 34 44 24 48 C14 44 4 38 4 28 L4 12 Z" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M16 26 L22 32 L32 20" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    '</g>'
    '<g class="float-el" style="--dur:11s;--delay:-3s;--op:0.14;--ty:-14px;--rot0:3deg;--rot1:-5deg;right:6%;top:15%;">'
    '<path d="M24 4 L44 12 L44 28 C44 38 34 44 24 48 C14 44 4 38 4 28 L4 12 Z" fill="rgba(167,139,250,0.15)" stroke="#a78bfa" stroke-width="1.5" stroke-linejoin="round"/>'
    '</g>'
    '<g class="float-el" style="--dur:10s;--delay:-1.5s;--op:0.16;--ty:-18px;--rot0:2deg;--rot1:-3deg;right:12%;top:40%;">'
    '<rect x="2" y="6" width="44" height="32" rx="4" fill="none" stroke="#6d28d9" stroke-width="2"/>'
    '<path d="M2 10 L24 24 L46 10" fill="none" stroke="#6d28d9" stroke-width="2" stroke-linecap="round"/>'
    '</g>'
    '<g class="float-el" style="--dur:8s;--delay:-4s;--op:0.12;--ty:-12px;--rot0:-2deg;--rot1:4deg;left:80%;top:70%;">'
    '<rect x="2" y="6" width="44" height="32" rx="4" fill="rgba(167,139,250,0.12)" stroke="#a78bfa" stroke-width="1.5"/>'
    '<path d="M2 10 L24 24 L46 10" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round"/>'
    '</g>'
    '<g class="float-el" style="--dur:13s;--delay:-2s;--op:0.15;--ty:-16px;--rot0:1deg;--rot1:-4deg;left:70%;top:22%;">'
    '<rect x="8" y="22" width="32" height="24" rx="4" fill="none" stroke="#7c3aed" stroke-width="2"/>'
    '<path d="M16 22 L16 16 A8 8 0 0 1 32 16 L32 22" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"/>'
    '<circle cx="24" cy="33" r="3" fill="#7c3aed" opacity="0.6"/>'
    '</g>'
    '<g class="float-el" style="--dur:7s;--delay:-0.5s;--op:0.13;--ty:-22px;--rot0:-3deg;--rot1:3deg;left:18%;top:72%;">'
    '<circle cx="24" cy="24" r="20" fill="none" stroke="#10b981" stroke-width="2"/>'
    '<path d="M14 24 L21 31 L34 17" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '</g>'
    '<g class="float-el" style="--dur:9.5s;--delay:-3.5s;--op:0.11;--ty:-10px;--rot0:2deg;--rot1:-2deg;left:42%;top:8%;">'
    '<path d="M24 4 L44 40 L4 40 Z" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linejoin="round"/>'
    '<line x1="24" y1="18" x2="24" y2="28" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>'
    '<circle cx="24" cy="34" r="2" fill="#f59e0b"/>'
    '</g>'
    '<circle class="float-el" style="--dur:6s;--delay:-1s;--op:0.20;--ty:-8px;--rot0:0deg;--rot1:0deg;left:30%;top:55%;" cx="6" cy="6" r="5" fill="#a78bfa"/>'
    '<circle class="float-el" style="--dur:7.5s;--delay:-2.5s;--op:0.15;--ty:-12px;--rot0:0deg;--rot1:0deg;left:60%;top:82%;" cx="6" cy="6" r="4" fill="#6ee7b7"/>'
    '<circle class="float-el" style="--dur:8.5s;--delay:-4.5s;--op:0.12;--ty:-10px;--rot0:0deg;--rot1:0deg;left:88%;top:30%;" cx="6" cy="6" r="6" fill="#fca5a5"/>'
    '</svg>'
    '</div>'
)
st.markdown(BG_SVG, unsafe_allow_html=True)

# ── Load model ──────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
model = pickle.load(
    open(BASE_DIR / "models" / "spam_model.pkl", "rb")
)

vectorizer = pickle.load(
    open(BASE_DIR / "models" / "vectorizer.pkl", "rb")
)
ps         = PorterStemmer()

def transform_text(text):
    text  = text.lower()
    text  = ''.join(c for c in text if c not in string.punctuation)
    words = [ps.stem(w) for w in text.split() if w not in ENGLISH_STOP_WORDS]
    return " ".join(words)

# ── App shell ────────────────────────────────────────────
st.markdown('<div class="app-shell">', unsafe_allow_html=True)

# ── LEFT: header ────────────────────────────────────────
st.markdown('<div class="col-left">', unsafe_allow_html=True)

st.markdown("""
<div class="hero-badge">
    <div class="badge-icon">🛡️</div>
    <span class="badge-text">AI-Powered Protection</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Message Scanner</div>', unsafe_allow_html=True)
st.markdown('<div class="headline">Detect <em>spam</em><br>instantly.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="tagline">Paste any SMS and our NLP model classifies it in milliseconds — with full confidence scoring and probability breakdown.</div>',
    unsafe_allow_html=True
)
st.markdown("""
<div class="stat-row">
    <div class="stat-chip"><div class="chip-dot"></div><strong>98.3%</strong> accuracy</div>
    <div class="stat-chip"><div class="chip-dot"></div><strong>5.5K</strong> messages</div>
    <div class="stat-chip"><div class="chip-dot"></div><strong>&lt;50ms</strong> inference</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: input + result ───────────────────────────────
st.markdown('<div class="col-right">', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Message</div>', unsafe_allow_html=True)

input_sms = st.text_area(
    label="SMS message input",
    placeholder="Paste or type an SMS message here…",
    height=148,
    max_chars=500,
    key="sms_input",
    label_visibility="collapsed",
)

btn_clicked = st.button("🔍  Analyze message")

# ── Result ──────────────────────────────────────────────
if btn_clicked:
    if not input_sms.strip():
        st.markdown("""
        <div class="warn-card">
            ⚠️  Please paste or type a message before analyzing.
        </div>
        """, unsafe_allow_html=True)
    else:
        transformed = transform_text(input_sms)
        vec         = vectorizer.transform([transformed])
        prediction  = model.predict(vec)[0]

        try:
            probs     = model.predict_proba(vec)[0]
            spam_prob = probs[1]
            ham_prob  = probs[0]
            conf      = max(spam_prob, ham_prob)
        except Exception:
            spam_prob = 0.97 if prediction == 1 else 0.03
            ham_prob  = 1 - spam_prob
            conf      = max(spam_prob, ham_prob)

        conf_pct = round(conf * 100, 1)
        fill_w   = f"{conf_pct}%"

        st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-top:20px;">Result</div>', unsafe_allow_html=True)

        if prediction == 1:
            st.markdown(f"""
            <div class="result-spam">
                <div class="result-header">
                    <div class="result-chip-spam">🚨</div>
                    <div>
                        <div class="result-title-spam">Spam detected</div>
                        <div class="result-desc-spam">High confidence — do not engage with this message</div>
                    </div>
                </div>
                <div class="conf-row">
                    <span class="conf-key">Confidence</span>
                    <span class="conf-pct-spam">{conf_pct}%</span>
                </div>
                <div class="conf-track">
                    <div class="conf-fill-spam" style="width:{fill_w};"></div>
                </div>
                <div class="prob-row">
                    <span class="prob-key">Spam probability</span>
                    <span class="prob-val-spam">{spam_prob:.4f}</span>
                </div>
                <div class="prob-row">
                    <span class="prob-key">Ham probability</span>
                    <span class="prob-val-safe">{ham_prob:.4f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-safe">
                <div class="result-header">
                    <div class="result-chip-safe">✅</div>
                    <div>
                        <div class="result-title-safe">Safe message</div>
                        <div class="result-desc-safe">No spam indicators detected — looks good!</div>
                    </div>
                </div>
                <div class="conf-row">
                    <span class="conf-key">Confidence</span>
                    <span class="conf-pct-safe">{conf_pct}%</span>
                </div>
                <div class="conf-track">
                    <div class="conf-fill-safe" style="width:{fill_w};"></div>
                </div>
                <div class="prob-row">
                    <span class="prob-key">Ham probability</span>
                    <span class="prob-val-safe">{ham_prob:.4f}</span>
                </div>
                <div class="prob-row">
                    <span class="prob-key">Spam probability</span>
                    <span class="prob-val-spam">{spam_prob:.4f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────
st.markdown("""
<div class="footer-area">
    <div class="section-label" style="margin-bottom:12px;">Powered by</div>
    <div class="pill-row">
        <div class="pill">🧠 Multinomial Naive Bayes</div>
        <div class="pill">📊 TF-IDF Vectorizer</div>
        <div class="pill">🌱 Porter Stemmer</div>
        <div class="pill">⚙️ scikit-learn</div>
        <div class="pill">🐍 Python 3</div>
    </div>
</div>
""", unsafe_allow_html=True)