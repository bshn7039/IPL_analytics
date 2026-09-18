"""
🤖 Page 7: AI Cricket Analyst
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
    .ai-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
        border-radius: 16px;
        padding: 1.6rem 2rem;
        border: 1px solid rgba(139, 92, 246, 0.35);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.5rem;
        margin-bottom: 0.3rem;
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-purple {
        background: rgba(139, 92, 246, 0.15);
        color: #C084FC;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    .badge-blue {
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .token-chip {
        font-size: 0.75rem;
        color: #94A3B8;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        display: inline-block;
        margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="ai-banner">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <div style="color:#A78BFA; font-weight:800; font-size:0.85rem; letter-spacing:0.08em; text-transform:uppercase;">
                🤖 CRICAI • PERFORMANCE INTELLIGENCE COPILOT
            </div>
            <h1 style="margin:0.2rem 0; font-size:2.3rem; color:#FFFFFF; font-weight:800;">
                AI Cricket Analyst
            </h1>
            <p style="margin:0; color:#94A3B8; font-size:0.95rem;">
                Ask any question regarding IPL statistics, tactical phase metrics, player records, or head-to-head franchise dynamics.
            </p>
        </div>
        <div style="text-align:right; margin-top:0.5rem;">
            <span class="status-badge badge-green">🛡️ IPL Guardrail Active</span>
            <span class="status-badge badge-purple">⚡ DeepSeek AI</span>
            <span class="status-badge badge-blue">🎯 Token-Optimized</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Secure API Key Check
existing_key = get_deepseek_api_key()

with st.sidebar:
    st.subheader("⚙️ AI Configuration")
    if existing_key:
        st.success("🔒 DeepSeek Key Active (Protected in `.env`)")
    else:
        st.warning("⚠️ No Key Found")
    
    custom_key = st.text_input("Override API Key (optional):", type="password", placeholder="sk-...")
    active_key = custom_key if custom_key else existing_key

    st.markdown("---")
    st.markdown("""
    **Guardrail Rules**:
    - Responds **only** to IPL & Cricket questions
    - Uses live database context snippets
    - Limits responses to save your token quota
    """)

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I am **CricAI**, your AI cricket analytics assistant. Ask me anything about IPL teams, players, match stats, head-to-head records, or strategies!", "usage": None}
    ]

# Starter Prompts Chips
st.markdown("##### 💡 Suggested Questions:")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

prompt_to_send = None
with p_col1:
    if st.button("🏏 Highest run-scorers in 2024?"):
        prompt_to_send = "Who are the leading run scorers in IPL 2024 and what were their strike rates?"
with p_col2:
    if st.button("🎯 Bumrah death overs impact?"):
        prompt_to_send = "How effective is Jasprit Bumrah in the death overs compared to powerplay?"
with p_col3:
    if st.button("⚔️ MI vs CSK head-to-head?"):
        prompt_to_send = "Compare Mumbai Indians (MI) vs Chennai Super Kings (CSK) head-to-head records and strength profiles."
with p_col4:
    if st.button("🪙 Does winning the toss help?"):
        prompt_to_send = "Does winning the toss significantly improve match winning chances in IPL games?"

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        if msg.get("usage"):
            u = msg["usage"]
            st.markdown(f"<div class='token-chip'>⚡ Tokens used: {u.get('total_tokens', 0)} (Prompt: {u.get('prompt_tokens', 0)} | Output: {u.get('completion_tokens', 0)})</div>", unsafe_allow_html=True)

# Handle Input from Chat or Starter Buttons
user_input = st.chat_input("Ask any question about IPL teams, players, or stats...") or prompt_to_send

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing IPL database & consulting DeepSeek..."):
            history_for_api = [m for m in st.session_state.messages if m["role"] in ["user", "assistant"]]
            response_data = ask_cricket_ai(user_input, chat_history=history_for_api[:-1], custom_api_key=active_key)
            
            st.markdown(response_data["reply"])
            if response_data.get("usage"):
                u = response_data["usage"]
                st.markdown(f"<div class='token-chip'>⚡ Tokens used: {u.get('total_tokens', 0)} (Prompt: {u.get('prompt_tokens', 0)} | Output: {u.get('completion_tokens', 0)})</div>", unsafe_allow_html=True)
            
            # Save assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["reply"],
                "usage": response_data.get("usage")
            })
