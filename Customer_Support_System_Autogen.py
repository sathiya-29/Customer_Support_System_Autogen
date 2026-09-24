import os
import asyncio
import time
import streamlit as st
from dotenv import load_dotenv

# 1. Load Environment Variables Silently
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# AutoGen v0.4 Imports
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMessageTermination, MaxMessageTermination
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

# 2. Page Configuration
st.set_page_config(
    page_title="Customer Support Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Custom CSS (White Chat Input, Black Font, and Dark UI Theme)
st.markdown("""
<style>
    /* Main App Dark Background */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    /* Chat Response Containers */
    div[data-testid="stChatMessage"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] span {
        color: #FFFFFF !important;
        font-size: 1rem !important;
    }

    /* CHAT INPUT BOX: WHITE BACKGROUND & BLACK FONT */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
    }

    /* Bottom Chat Area Container */
    div[data-testid="stBottom"] {
        background-color: #0F172A !important;
    }

    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
    }

    /* Specialist Badges */
    .agent-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .badge-billing { background-color: #6B21A8; color: #F3E8FF !important; border: 1px solid #A855F7; }
    .badge-tech { background-color: #065F46; color: #D1FAE5 !important; border: 1px solid #10B981; }
    .badge-account { background-color: #1E40AF; color: #DBEAFE !important; border: 1px solid #3B82F6; }
    .badge-shipping { background-color: #854D0E; color: #FEF9C3 !important; border: 1px solid #EAB308; }
    .badge-general { background-color: #374151; color: #F9FAFB !important; border: 1px solid #9CA3AF; }

    /* Sidebar Description Cards */
    .agent-desc-card {
        background-color: #1E293B;
        border-left: 3px solid #475569;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .agent-desc-card p {
        margin: 0;
        font-size: 0.78rem !important;
        color: #94A3B8 !important;
        line-height: 1.3 !important;
    }

    /* Preset Scenario Buttons */
    .stButton > button {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        background-color: #334155 !important;
        border-color: #38BDF8 !important;
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. Sidebar Controls & Agent Descriptions
with st.sidebar:
    st.title("⚙️ System Control")
    st.markdown("---")
    st.subheader("🔒 Security Status")
    if api_key:
        st.success("API Key Active (.env)")
        st.caption("Key loaded silently in memory.")
    else:
        st.error("OPENAI_API_KEY Missing in `.env`")

    st.markdown("---")
    st.subheader("🎯 Specialist Scope")
    
    # Billing Agent Scope
    st.markdown("""
    <span class="agent-badge badge-billing">💳 Billing_Agent</span>
    <div class="agent-desc-card">
        <p><b>Scope:</b> Payments, invoices, subscriptions, refunds, and double charges.</p>
    </div>
    """, unsafe_allow_html=True)

    # Tech Support Agent Scope
    st.markdown("""
    <span class="agent-badge badge-tech">🛠️ TechSupport_Agent</span>
    <div class="agent-desc-card">
        <p><b>Scope:</b> Platform bugs, API errors, system crashes, and code troubleshooting.</p>
    </div>
    """, unsafe_allow_html=True)

    # Account Agent Scope
    st.markdown("""
    <span class="agent-badge badge-account">🔐 Account_Agent</span>
    <div class="agent-desc-card">
        <p><b>Scope:</b> User login, password resets, MFA/2FA lockouts, and account security.</p>
    </div>
    """, unsafe_allow_html=True)

    # Shipping Agent Scope
    st.markdown("""
    <span class="agent-badge badge-shipping">📦 Shipping_Agent</span>
    <div class="agent-desc-card">
        <p><b>Scope:</b> Physical delivery rates, order tracking, couriers, and dispatch costs.</p>
    </div>
    """, unsafe_allow_html=True)

    # General Info Agent Scope
    st.markdown("""
    <span class="agent-badge badge-general">ℹ️ GeneralInfo_Agent</span>
    <div class="agent-desc-card">
        <p><b>Scope:</b> General knowledge, AI/tech updates, company info, and unclassified FAQs.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# 5. Header Area
st.markdown("""
<div class="header-box">
    <h2 style="margin:0; color:#F8FAFC;">🤖 Customer Support Multi-Agent System</h2>
    <p style="margin-top:8px; color:#94A3B8; font-size:1.05rem;">
        Powered by <b>AutoGen v0.4</b> & <b>gpt-4o-mini</b>.
    </p>
</div>
""", unsafe_allow_html=True)

# Preset Scenario Buttons
st.markdown("##### ⚡ Quick Test Scenarios")
col1, col2, col3, col4 = st.columns(4)
selected_preset = None

if col1.button("💳 Billing Double Charge", use_container_width=True):
    selected_preset = "I was charged twice for my subscription this month. How do I get a refund?"
if col2.button("🛠️ API Error / Crash", use_container_width=True):
    selected_preset = "My application throws a 500 internal server error when exporting reports."
if col3.button("🔐 Reset MFA / Password", use_container_width=True):
    selected_preset = "I lost my phone and cannot log in with two-factor authentication."
if col4.button("📦 Delivery Cost Query", use_container_width=True):
    selected_preset = "what is the delivery cost"

# 6. AutoGen v0.4 Routing Engine (Fixed Selector Function)
async def run_autogen_support_pipeline(current_query: str):
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0.0
    )

    term_inst = "\n\nEnd your response with 'TERMINATE'."

    shipping_agent = AssistantAgent(
        name="Shipping_Agent",
        model_client=model_client,
        description="Handles physical delivery, shipping costs, tracking, and couriers.",
        system_message="You are a Shipping & Delivery Logistics Specialist. Answer delivery and shipping cost queries directly." + term_inst
    )

    billing_agent = AssistantAgent(
        name="Billing_Agent",
        model_client=model_client,
        description="Handles invoices, double charges, payment refunds, and account billing disputes.",
        system_message="You are a Billing Support Specialist. Answer payment, invoice, and subscription billing queries." + term_inst
    )

    tech_agent = AssistantAgent(
        name="TechSupport_Agent",
        model_client=model_client,
        description="Handles technical bugs, software errors, 500 server crashes, code issues, and API troubleshooting.",
        system_message="You are a Technical Support Specialist. Provide technical debugging guidance." + term_inst
    )

    account_agent = AssistantAgent(
        name="Account_Agent",
        model_client=model_client,
        description="Handles user account login access, password resets, MFA/2FA lockouts, and profile security.",
        system_message="You are an Account Security Specialist. Provide clear account recovery steps." + term_inst
    )

    general_agent = AssistantAgent(
        name="GeneralInfo_Agent",
        model_client=model_client,
        description="Handles general knowledge, AI updates, news, weather, or company overviews.",
        system_message="You are a General Support Specialist. Answer general queries, news, or general knowledge requests accurately." + term_inst
    )

    termination = TextMessageTermination("TERMINATE") | MaxMessageTermination(max_messages=5)

    # Custom Selector Rule Function (Eliminates "Model failed to select a speaker after 3" retries)
    def custom_selector(messages):
        last_message = ""
        for m in reversed(messages):
            if hasattr(m, "content") and isinstance(m.content, str) and m.content:
                last_message = m.content.lower()
                break

        if any(w in last_message for w in ["delivery", "shipping", "courier", "package", "tracking", "dispatch"]):
            return "Shipping_Agent"
        elif any(w in last_message for w in ["invoice", "refund", "subscription", "double charge", "charge", "payment", "card"]):
            return "Billing_Agent"
        elif any(w in last_message for w in ["error", "bug", "crash", "api", "500", "code", "exception"]):
            return "TechSupport_Agent"
        elif any(w in last_message for w in ["password", "login", "mfa", "2fa", "locked", "account"]):
            return "Account_Agent"
        else:
            return "GeneralInfo_Agent"

    team = SelectorGroupChat(
        participants=[shipping_agent, billing_agent, tech_agent, account_agent, general_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_func=custom_selector
    )

    final_response = ""
    selected_agent_name = "GeneralInfo_Agent"

    async for message in team.run_stream(task=current_query):
        if hasattr(message, "source") and message.source != "user":
            selected_agent_name = message.source
        if hasattr(message, "content") and isinstance(message.content, str):
            final_response = message.content

    clean_response = final_response.replace("TERMINATE", "").strip()
    return selected_agent_name, clean_response


# 7. Execution Loop
user_input = st.chat_input("Type your support query here...")
if selected_preset:
    user_input = selected_preset

# Display Chat History
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["query"])
    with st.chat_message("assistant"):
        b_class = "badge-general"
        if "Billing" in chat["agent"]: b_class = "badge-billing"
        elif "Tech" in chat["agent"]: b_class = "badge-tech"
        elif "Account" in chat["agent"]: b_class = "badge-account"
        elif "Shipping" in chat["agent"]: b_class = "badge-shipping"

        st.markdown(f'<span class="agent-badge {b_class}">Selected Specialist: {chat["agent"]}</span>', unsafe_allow_html=True)
        st.write(chat["response"])
        st.caption(f"⚡ Execution time: {chat['latency']:.2f}s")

# Process Request
if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Please ensure your `OPENAI_API_KEY` is present in your `.env` file.")
        elif not AUTOGEN_AVAILABLE:
            st.error("AutoGen packages are not available in this virtual environment.")
        else:
            with st.spinner("🤖 Evaluating query and selecting specialist..."):
                t_start = time.time()
                agent_name, response_text = asyncio.run(run_autogen_support_pipeline(user_input))
                t_elapsed = time.time() - t_start

            b_class = "badge-general"
            if "Billing" in agent_name: b_class = "badge-billing"
            elif "Tech" in agent_name: b_class = "badge-tech"
            elif "Account" in agent_name: b_class = "badge-account"
            elif "Shipping" in agent_name: b_class = "badge-shipping"

            st.markdown(f'<span class="agent-badge {b_class}">Selected Specialist: {agent_name}</span>', unsafe_allow_html=True)
            st.write(response_text)
            st.caption(f"⚡ Executed in {t_elapsed:.2f}s via AutoGen v0.4 SelectorGroupChat")

            st.session_state.chat_history.append({
                "query": user_input,
                "agent": agent_name,
                "response": response_text,
                "latency": t_elapsed
            })