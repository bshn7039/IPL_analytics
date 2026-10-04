"""
Page 7: AI Cricket Analyst
Natural language cricket intelligence assistant powered by DeepSeek.
Features:
- Strict IPL domain guardrails (only responds to cricket questions)
- Context-aware dynamic database retrieval
- Strict token-budget optimization (< 250 prompt tokens/query)
- Interactive prompt chips and token usage telemetry
"""
import streamlit as st
from analytics.ai_assistant import ask_cricket_ai, get_deepseek_api_key
from analytics.ui_styles import apply_custom_styles

st.set_page_config(page_title="AI Cricket Analyst | IPL Hub", page_icon="🤖", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #130C2E 0%, #1D1344 60%, #0A061C 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(168, 85, 247, 0.22);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(168, 85, 247, 0.12) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #C084FC;
    margin-bottom: 0.5rem;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
}
.telemetry-chip-purple {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(168, 85, 247, 0.12);
    color: #D8B4FE;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
.telemetry-chip-green {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(16, 185, 129, 0.12);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.telemetry-chip-blue {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(6, 182, 212, 0.12);
    color: #67E8F9;
    border: 1px solid rgba(6, 182, 212, 0.3);
}
.token-chip {
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.04);
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-top: 0.4rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">AI Copilot 07</div>
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
<div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">DeepSeek Cricket Intelligence Copilot</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">High-precision natural language queries augmented with real-time relational IPL database telemetry and phase benchmarks.</p>
</div>
<div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
<span class="telemetry-chip-green">Guardrails Active</span>
<span class="telemetry-chip-purple">DeepSeek V3</span>
<span class="telemetry-chip-blue">Token Optimized</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── API Key Configuration ─────────────────────────────────────────────────────
existing_key = get_deepseek_api_key()

with st.sidebar:
    st.markdown('<div class="section-label">Engine Configuration</div>', unsafe_allow_html=True)
    if existing_key:
        st.markdown('<span class="telemetry-chip-green">DeepSeek Key Verified</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="telemetry-chip-purple">Key Missing (.env)</span>', unsafe_allow_html=True)

    custom_key = st.text_input("Override API Key", type="password", placeholder="sk-...")
    active_key = custom_key if custom_key else existing_key

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("""
    **Operational Parameters:**
    - Domain: Indian Premier League records
    - Retrievable schemas: Match, Batting, Bowling
    - Target prompt budget: <250 tokens
    """)

    if st.button("Reset Session History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Initialize State ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **CricAI Intelligence**. Query me on franchise form, player head-to-head metrics, death-over economies, or toss correlations.", "usage": None}
    ]

# ── Preset Query Chips ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Suggested Intelligence Inquiries</div>', unsafe_allow_html=True)
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

prompt_to_send = None
with p_col1:
    if st.button("Highest run-scorers in 2024?", use_container_width=True):
        prompt_to_send = "Who are the leading run scorers in IPL 2024 and what were their strike rates?"
with p_col2:
    if st.button("Jasprit Bumrah death overs impact?", use_container_width=True):
        prompt_to_send = "How effective is Jasprit Bumrah in the death overs compared to powerplay?"
with p_col3:
    if st.button("MI vs CSK head-to-head records?", use_container_width=True):
        prompt_to_send = "Compare Mumbai Indians (MI) vs Chennai Super Kings (CSK) head-to-head records and strength profiles."
with p_col4:
    if st.button("Toss conversion win statistics?", use_container_width=True):
        prompt_to_send = "Does winning the toss significantly improve match winning chances in IPL games?"

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Chat Display ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("usage"):
            u = msg["usage"]
            st.markdown(f"<div class='token-chip'>TELEMETRY: {u.get('total_tokens', 0)} tokens (Prompt: {u.get('prompt_tokens', 0)} | Completion: {u.get('completion_tokens', 0)})</div>", unsafe_allow_html=True)

# ── Chat Execution ────────────────────────────────────────────────────────────
user_input = st.chat_input("Inquire regarding batting, bowling, matches or tactical strategies...") or prompt_to_send

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving database telemetry and evaluating prompt..."):
            history_for_api = [m for m in st.session_state.messages if m["role"] in ["user", "assistant"]]
            response_data = ask_cricket_ai(user_input, chat_history=history_for_api[:-1], custom_api_key=active_key)

            st.markdown(response_data["reply"])
            if response_data.get("usage"):
                u = response_data["usage"]
                st.markdown(f"<div class='token-chip'>TELEMETRY: {u.get('total_tokens', 0)} tokens (Prompt: {u.get('prompt_tokens', 0)} | Completion: {u.get('completion_tokens', 0)})</div>", unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["reply"],
                "usage": response_data.get("usage")
            })
