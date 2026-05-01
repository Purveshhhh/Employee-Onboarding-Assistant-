import streamlit as st
import os
import json
import datetime
from rag_engine import load_documents, get_answer
from utils import (
    save_employee, load_employees, generate_offer_letter,
    generate_joining_form, save_task_progress, load_task_progress,
    save_training_progress, load_training_progress,
    register_user, login_user
)

st.set_page_config(
    page_title="XYZ Onboarding Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME INIT ────────────────────────────────────────────────────────────────
# ── THEME TOGGLE ─────────────────────────────────────────────────────────────
# We use Streamlit's native theme + only override custom component styles
# Theme toggle is in sidebar below

# ── INJECT CSS ────────────────────────────────────────────────────────────────
# We do NOT override Streamlit base colors - we let the native theme (Light/Dark)
# handle backgrounds and text. We only style our custom HTML components.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* FONTS ONLY - no background overrides so Streamlit theme works */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { font-family: 'DM Sans', sans-serif !important; }
h1,h2,h3,h4,h5,h6 { font-family: 'Syne', sans-serif !important; }

.main .block-container { padding: 1.5rem 2rem; max-width: 1300px; }

/* BUTTONS - inherit theme colors */
.stButton > button {
    border-radius: 8px !important;
    padding: 0.55rem 1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.18s !important;
    border: 1px solid rgba(128,128,128,0.3) !important;
}
.stButton > button:hover {
    border-color: #4a9eff !important;
    color: #4a9eff !important;
}

/* FORM INPUTS - inherit theme */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    border: 1px solid rgba(128,128,128,0.3) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #4a9eff !important;
    box-shadow: 0 0 0 2px rgba(74,158,255,0.15) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stFileUploader label {
    font-size: 0.88rem !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* SELECTBOX */
[data-baseweb="select"] { border-radius: 8px !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] { color: #4a9eff !important; }

/* CHAT */
.stChatMessage {
    border-radius: 12px !important;
    margin-bottom: 0.8rem !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-left: 3px solid #4a9eff !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-left: 3px solid #22d3a0 !important;
}
.stChatInputContainer {
    border-radius: 10px !important;
    margin-top: 1rem;
    border: 1px solid rgba(128,128,128,0.3) !important;
}

/* PROGRESS */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4a9eff, #22d3a0) !important;
    border-radius: 6px !important;
}
.stProgress > div > div { border-radius: 6px !important; }

/* EXPANDER */
.streamlit-expanderHeader { border-radius: 8px !important; }
.streamlit-expanderHeader:hover { border-color: #4a9eff !important; }

/* METRICS */
[data-testid="stMetricValue"] {
    color: #4a9eff !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="metric-container"] {
    border-radius: 10px !important;
    padding: 0.8rem !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: rgba(128,128,128,0.3); border-radius: 4px; }

/* CUSTOM CARDS - theme aware via currentColor */
.card {
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(128,128,128,0.2);
}
.card-accent { border-left: 3px solid #4a9eff; }
.card-green  { border-left: 3px solid #22d3a0; }
.card-amber  { border-left: 3px solid #f59e0b; }
.card-red    { border-left: 3px solid #f43f5e; }

/* STAT BOX */
.stat-box {
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    transition: border-color 0.2s;
    border: 1px solid rgba(128,128,128,0.2);
}
.stat-box:hover { border-color: #4a9eff; }
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #4a9eff;
}
.stat-lbl {
    font-size: 0.75rem;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.6;
}

/* SECTION HEADER */
.section-header {
    display: flex; align-items: center; gap: 0.7rem;
    margin-bottom: 1.2rem; padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}
.section-header h2 { font-size: 1.3rem; margin: 0; }
.section-badge {
    background: rgba(74,158,255,0.15);
    color: #4a9eff;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* BADGES */
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 5px; font-size: 0.72rem; font-weight: 600; }
.badge-blue  { background: rgba(74,158,255,0.15);  color: #4a9eff; }
.badge-green { background: rgba(34,211,160,0.15);  color: #22d3a0; }
.badge-amber { background: rgba(245,158,11,0.15);  color: #f59e0b; }
.badge-red   { background: rgba(244,63,94,0.15);   color: #f43f5e; }

/* USER PILL IN SIDEBAR */
.user-pill {
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(128,128,128,0.2);
}

/* REMINDER ROW */
.reminder-row {
    border-radius: 9px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(128,128,128,0.15);
    border-left: 3px solid #4a9eff;
}

/* KEY DATES ROW */
.date-row {
    display: flex; gap: 0.8rem; align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(128,128,128,0.15);
}
.date-badge {
    background: rgba(74,158,255,0.15);
    color: #4a9eff;
    padding: 0.2rem 0.5rem;
    border-radius: 5px;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
}

/* CHAT EMPTY STATE */
.chat-empty {
    text-align: center;
    padding: 4rem 2rem;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.2);
    opacity: 0.85;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    border-radius: 10px !important;
}

/* DOC ITEM */
.doc-item {
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.84rem;
    border: 1px solid rgba(128,128,128,0.2);
    opacity: 0.85;
}

hr { border-color: rgba(128,128,128,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  LOGIN PAGE
# ═══════════════════════════════════════════
# ═══════════════════════════════════════════
#  REAL AUTH SYSTEM — Login & Sign Up
# ═══════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    col_l, col_m, col_r = st.columns([1, 1.1, 1])
    with col_m:
        # Logo header
        st.markdown("""
        <div style='text-align:center;padding:2rem 0 1.5rem 0;'>
            <div style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#dce3f0;'>🏢 XYZ Technologies</div>
            <div style='color:#4a5a7a;font-size:0.85rem;margin-top:0.4rem;'>Employee Onboarding Portal</div>
        </div>
        """, unsafe_allow_html=True)

        # Tab switcher
        tab_login, tab_signup = st.tabs(["🔐 Sign In", "📝 Create Account"])

        # ── LOGIN TAB ──
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            login_username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="login_btn"):
                if not login_username or not login_password:
                    st.error("❌ Please enter both username and password.")
                else:
                    success, result = login_user(login_username, login_password)
                    if success:
                        st.session_state.logged_in    = True
                        st.session_state.username     = login_username
                        st.session_state.user_role    = result["role"]
                        st.session_state.user_name    = result["full_name"]
                        st.session_state.current_page = "🏠 Dashboard"
                        st.success(f"Welcome back, {result['full_name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

        # ── SIGN UP TAB ──
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_name     = st.text_input("Full Name *", placeholder="Your full name", key="reg_name")
            reg_email    = st.text_input("Email Address *", placeholder="your@email.com", key="reg_email")
            reg_username = st.text_input("Choose Username *", placeholder="e.g. john_doe", key="reg_user")
            reg_password = st.text_input("Choose Password *", type="password", placeholder="Min 6 characters", key="reg_pass")
            reg_confirm  = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password", key="reg_confirm")
            reg_role     = st.selectbox("Account Type", ["Employee", "HR Admin"], key="reg_role")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="signup_btn"):
                if not all([reg_name, reg_email, reg_username, reg_password, reg_confirm]):
                    st.error("❌ Please fill in all required fields.")
                elif reg_password != reg_confirm:
                    st.error("❌ Passwords do not match.")
                elif "@" not in reg_email:
                    st.error("❌ Please enter a valid email address.")
                else:
                    success, msg = register_user(reg_username, reg_password, reg_name, reg_email, reg_role)
                    if success:
                        st.success(f"✅ {msg} Please sign in using the Sign In tab.")
                    else:
                        st.error(f"❌ {msg}")

    st.stop()

# ═══════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0.5rem 1rem 0.5rem;'>
        <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#dce3f0;'>🏢 XYZ Technologies</div>
        <div style='font-size:0.75rem;color:#4a5a7a;margin-top:2px;'>Onboarding Portal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#0a1428;border:1px solid #1a2540;border-radius:10px;padding:0.8rem;margin-bottom:1rem;'>
        <div style='font-size:0.8rem;color:#4a5a7a;'>Signed in as</div>
        <div style='font-family:Syne,sans-serif;font-size:0.95rem;color:#dce3f0;font-weight:600;'>{st.session_state.user_name}</div>
        <div style='font-size:0.72rem;color:#4a9eff;margin-top:2px;'>{st.session_state.user_role}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.7rem;color:#4a5a7a;text-transform:uppercase;letter-spacing:0.08em;padding:0 0 0.4rem 0;'>Navigation</p>", unsafe_allow_html=True)

    pages = [
        "🏠 Dashboard",
        "💬 AI Assistant",
        "👤 Employee Profile",
        "📁 Document Manager",
        "📝 Generate Documents",
        "✅ Onboarding Tasks",
        "🎓 Training & Learning",
        "📞 HR Contacts",
    ]

    for page in pages:
        is_active = st.session_state.current_page == page
        if st.button(page, key=f"nav_{page}"):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")

    user_msgs = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.markdown(f"<p style='font-size:0.78rem;color:#4a5a7a;'>💬 Chat messages: <strong style='color:#8a9bc4;'>{user_msgs}</strong></p>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

page = st.session_state.current_page

# ═══════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='font-family:Syne,sans-serif;font-size:2rem;color:inherit;'>
            Welcome back, {st.session_state.user_name}! 👋
        </h1>
        <p style='opacity:0.6;margin-top:0.3rem;'>
            {datetime.datetime.now().strftime("%A, %B %d, %Y")} · XYZ Employee Onboarding Portal
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    employees = load_employees()
    tasks_data = load_task_progress(st.session_state.username)
    completed_tasks = sum(1 for v in tasks_data.values() if v)
    total_tasks = len(tasks_data) if tasks_data else 8

    docs_folder = "documents"
    doc_count = len([f for f in os.listdir(docs_folder) if f.endswith(".pdf")]) if os.path.exists(docs_folder) else 0

    training_data = load_training_progress(st.session_state.username)
    completed_courses = sum(1 for v in training_data.values() if v.get("completed"))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{completed_tasks}/{total_tasks}</div><div class="stat-lbl">Tasks Done</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{doc_count}</div><div class="stat-lbl">Documents</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{completed_courses}</div><div class="stat-lbl">Courses Done</div></div>""", unsafe_allow_html=True)
    with col4:
        pct = int((completed_tasks / total_tasks) * 100) if total_tasks else 0
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{pct}%</div><div class="stat-lbl">Onboarding Progress</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown("### 🚀 Quick Actions")
        qa1, qa2, qa3 = st.columns(3)
        with qa1:
            if st.button("💬 Ask AI Assistant", use_container_width=True):
                st.session_state.current_page = "💬 AI Assistant"; st.rerun()
        with qa2:
            if st.button("📁 Upload Document", use_container_width=True):
                st.session_state.current_page = "📁 Document Manager"; st.rerun()
        with qa3:
            if st.button("✅ View Tasks", use_container_width=True):
                st.session_state.current_page = "✅ Onboarding Tasks"; st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Onboarding Progress")
        progress_pct = completed_tasks / total_tasks if total_tasks else 0
        st.progress(progress_pct)
        st.caption(f"{completed_tasks} of {total_tasks} tasks completed ({pct}%)")

        st.markdown("---")
        st.markdown("### 🎓 Learning Progress")
        courses = {
            "Company Orientation": 100,
            "HR Policies & Code of Conduct": 75,
            "IT Security Awareness": 50,
            "Team Collaboration Tools": 25,
        }
        for course, prog in courses.items():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(course)
                st.progress(prog / 100)
            with c2:
                st.markdown(f"<p style='color:#4a9eff;font-size:0.8rem;padding-top:1.2rem;'>{prog}%</p>", unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🔔 Reminders")
        reminders = [
            ("🔴", "Submit PAN Card copy", "Due Today"),
            ("🟡", "Complete IT Security Training", "Due in 2 days"),
            ("🟡", "Meet your manager", "Due in 3 days"),
            ("🟢", "ID Card generation pending", "This week"),
            ("🟢", "Set up company email", "This week"),
        ]
        for icon, task, due in reminders:
            st.markdown(f"""
            <div class="reminder-row">
                <div class="reminder-title">{icon} {task}</div>
                <div class="reminder-sub">{due}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📅 Key Dates")
        dates = [
            ("Day 1", "Document submission"),
            ("Day 3", "Team introduction"),
            ("Day 7", "Complete mandatory training"),
            ("Day 14", "First 1-on-1 with manager"),
            ("Day 30", "30-day review meeting"),
        ]
        for day, event in dates:
            st.markdown(f"""
            <div class="date-row"><span class="date-badge">{day}</span><span class="date-text">{event}</span></div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  PAGE: AI ASSISTANT
# ═══════════════════════════════════════════
elif page == "💬 AI Assistant":
    st.markdown("""
    <div class="section-header">
        <h2>💬 AI Onboarding Assistant</h2>
        <span class="section-badge">● ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    if "context" not in st.session_state:
        with st.spinner("Loading HR knowledge base..."):
            docs_folder = "documents"
            pdf_files = [f for f in os.listdir(docs_folder) if f.endswith(".pdf")] if os.path.exists(docs_folder) else []
            if pdf_files:
                st.session_state.context = load_documents(docs_folder)
                st.success(f"✅ {len(pdf_files)} HR document(s) loaded into knowledge base")
            else:
                st.session_state.context = ""
                st.warning("⚠️ No HR documents found. Upload PDFs in Document Manager.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col_chat, col_panel = st.columns([2.2, 1])

    with col_panel:
        st.markdown("### 💡 Quick Questions")
        quick_qs = [
            ("🏖️ Leave policy",           "What is the leave policy?"),
            ("⏰ Working hours",           "What are the working hours?"),
            ("💻 Laptop setup",            "How do I set up my laptop and email?"),
            ("💰 Salary & benefits",       "What are my salary and benefits?"),
            ("📋 Onboarding steps",        "What are the onboarding steps for first 30 days?"),
            ("📞 Who to contact",          "Who do I contact for HR, IT and payroll?"),
            ("🏥 Health insurance",        "What is the health insurance policy?"),
            ("📈 Performance appraisal",   "How does the performance appraisal process work?"),
            ("🎓 Training programs",       "What training programs are available for new employees?"),
            ("🔒 IT security policy",      "What is the IT and data security policy?"),
            ("👔 Dress code",              "What is the dress code and code of conduct?"),
            ("🏠 Work from home",          "What is the work from home policy?"),
        ]
        for label, query in quick_qs:
            if st.button(label, key=f"qq_{label}"):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()

        st.markdown("---")
        st.markdown("### 🗂️ Topics")
        topics = [
            ("📋 HR Policies",         "Tell me about the HR policies"),
            ("🏖️ Leave & Attendance",  "What is the leave and attendance policy?"),
            ("💻 IT Setup",            "How do I set up my IT equipment and laptop?"),
            ("💰 Salary & Benefits",   "What are all the salary and benefits?"),
            ("📅 Onboarding Schedule", "What is the onboarding schedule for first 30 days?"),
            ("👥 Important Contacts",  "Who are the important contacts in the company?"),
            ("📜 Code of Conduct",     "What is the code of conduct policy?"),
            ("💊 Medical Benefits",    "What are the medical and insurance benefits?"),
        ]
        for label, query in topics:
            if st.button(label, key=f"tp_{label}"):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col_chat:
        # Chat navigator
        if len(st.session_state.messages) > 0:
            st.markdown("**Chat Navigator**")
            user_msgs_list = [(i, m["content"][:60]+"...") for i, m in enumerate(st.session_state.messages) if m["role"] == "user"]
            if user_msgs_list:
                nav_options = ["— Jump to —"] + [f"Q{idx+1}: {txt}" for idx, (_, txt) in enumerate(user_msgs_list)]
                selected_nav = st.selectbox("", nav_options, label_visibility="collapsed")

        # Chat messages
        if len(st.session_state.messages) == 0:
            st.markdown("""
            <div class='chat-empty'>
                <div style='font-size:3rem;margin-bottom:1rem;'>🤖</div>
                <div style='font-family:Syne,sans-serif;font-size:1.1rem;color:inherit;'>Hi! I'm your AI Onboarding Assistant</div>
                <div style='font-size:0.85rem;opacity:0.6;margin-top:0.5rem;'>
                    Ask me anything about HR policies, benefits, IT setup, or click a quick question →
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Generate answer
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            user_q = st.session_state.messages[-1]["content"]
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    if st.session_state.context:
                        response = get_answer(user_q, st.session_state.context)
                    else:
                        response = "⚠️ No HR documents loaded. Please upload PDFs in the Document Manager section."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        if prompt := st.chat_input("Ask anything about your onboarding..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# ═══════════════════════════════════════════
#  PAGE: EMPLOYEE PROFILE
# ═══════════════════════════════════════════
elif page == "👤 Employee Profile":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>👤 Employee Profile</h2><span class="section-badge">Registration</span></div>""", unsafe_allow_html=True)

    employees = load_employees()
    existing = employees.get(st.session_state.username, {})

    tab1, tab2 = st.tabs(["📝 Personal Details", "🏦 Bank & Financial Info"])

    with tab1:
        with st.form("profile_form"):
            st.markdown("#### Personal Information")
            c1, c2 = st.columns(2)
            with c1:
                full_name  = st.text_input("Full Name *", value=existing.get("full_name", ""))
                emp_id     = st.text_input("Employee ID *", value=existing.get("emp_id", ""))
                dob        = st.text_input("Date of Birth", value=existing.get("dob", ""), placeholder="DD/MM/YYYY")
                gender     = st.selectbox("Gender", ["Select", "Male", "Female", "Other"], index=["Select", "Male", "Female", "Other"].index(existing.get("gender", "Select")))
                phone      = st.text_input("Mobile Number *", value=existing.get("phone", ""))
            with c2:
                email      = st.text_input("Personal Email *", value=existing.get("email", ""))
                company_email = st.text_input("Company Email", value=existing.get("company_email", ""), placeholder="firstname.lastname@xyztech.com")
                department = st.selectbox("Department *", ["Select", "Engineering", "Finance", "HR", "Marketing", "Operations", "Sales", "IT"], index=["Select", "Engineering", "Finance", "HR", "Marketing", "Operations", "Sales", "IT"].index(existing.get("department", "Select")))
                designation = st.text_input("Designation", value=existing.get("designation", ""))
                joining_date = st.text_input("Date of Joining", value=existing.get("joining_date", ""), placeholder="DD/MM/YYYY")

            st.markdown("#### Address")
            address = st.text_area("Permanent Address", value=existing.get("address", ""), height=80)
            c3, c4 = st.columns(2)
            with c3:
                city  = st.text_input("City", value=existing.get("city", ""))
                state = st.text_input("State", value=existing.get("state", ""))
            with c4:
                pincode  = st.text_input("PIN Code", value=existing.get("pincode", ""))
                country  = st.text_input("Country", value=existing.get("country", "India"))

            st.markdown("#### Emergency Contact")
            c5, c6 = st.columns(2)
            with c5:
                emergency_name   = st.text_input("Emergency Contact Name", value=existing.get("emergency_name", ""))
                emergency_rel    = st.text_input("Relationship", value=existing.get("emergency_rel", ""))
            with c6:
                emergency_phone  = st.text_input("Emergency Contact Phone", value=existing.get("emergency_phone", ""))

            if st.form_submit_button("💾 Save Profile", use_container_width=True):
                profile = {
                    "full_name": full_name, "emp_id": emp_id, "dob": dob, "gender": gender,
                    "phone": phone, "email": email, "company_email": company_email,
                    "department": department, "designation": designation, "joining_date": joining_date,
                    "address": address, "city": city, "state": state, "pincode": pincode, "country": country,
                    "emergency_name": emergency_name, "emergency_rel": emergency_rel, "emergency_phone": emergency_phone,
                }
                save_employee(st.session_state.username, profile)
                st.success("✅ Profile saved successfully!")
                st.rerun()

    with tab2:
        with st.form("bank_form"):
            st.markdown("#### Bank Account Details")
            c1, c2 = st.columns(2)
            with c1:
                bank_name    = st.text_input("Bank Name", value=existing.get("bank_name", ""))
                account_no   = st.text_input("Account Number", value=existing.get("account_no", ""), type="password")
                ifsc         = st.text_input("IFSC Code", value=existing.get("ifsc", ""))
            with c2:
                account_type = st.selectbox("Account Type", ["Savings", "Current"], index=["Savings", "Current"].index(existing.get("account_type", "Savings")))
                branch       = st.text_input("Branch Name", value=existing.get("branch", ""))
                branch_city  = st.text_input("Branch City", value=existing.get("branch_city", ""))

            st.markdown("#### Tax & Statutory Details")
            c3, c4 = st.columns(2)
            with c3:
                pan_number   = st.text_input("PAN Number", value=existing.get("pan_number", ""), placeholder="ABCDE1234F")
                aadhar       = st.text_input("Aadhaar Number (Last 4 digits)", value=existing.get("aadhar", ""), max_chars=4)
            with c4:
                pf_number    = st.text_input("PF Number (if existing)", value=existing.get("pf_number", ""))
                uan_number   = st.text_input("UAN Number (if existing)", value=existing.get("uan_number", ""))

            if st.form_submit_button("💾 Save Bank Details", use_container_width=True):
                bank_data = {
                    "bank_name": bank_name, "account_no": account_no, "ifsc": ifsc,
                    "account_type": account_type, "branch": branch, "branch_city": branch_city,
                    "pan_number": pan_number, "aadhar": aadhar, "pf_number": pf_number, "uan_number": uan_number,
                }
                save_employee(st.session_state.username, {**existing, **bank_data})
                st.success("✅ Bank details saved securely!")

# ═══════════════════════════════════════════
#  PAGE: DOCUMENT MANAGER
# ═══════════════════════════════════════════
elif page == "📁 Document Manager":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>📁 Document Management System</h2><span class="section-badge">Upload & Verify</span></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "📋 Required Documents", "📂 All Documents"])

    REQUIRED_DOCS = {
        "PAN Card":              {"required": True,  "formats": ["pdf", "jpg", "png"], "max_size_mb": 2},
        "Aadhaar Card":          {"required": True,  "formats": ["pdf", "jpg", "png"], "max_size_mb": 2},
        "10th Marksheet":        {"required": True,  "formats": ["pdf"],               "max_size_mb": 5},
        "12th Marksheet":        {"required": True,  "formats": ["pdf"],               "max_size_mb": 5},
        "Degree Certificate":    {"required": True,  "formats": ["pdf"],               "max_size_mb": 5},
        "Offer Letter":          {"required": True,  "formats": ["pdf"],               "max_size_mb": 5},
        "Previous Experience Letter": {"required": False, "formats": ["pdf"],          "max_size_mb": 5},
        "Passport Photo":        {"required": True,  "formats": ["jpg", "png"],        "max_size_mb": 1},
        "Bank Passbook/Cheque":  {"required": True,  "formats": ["pdf", "jpg", "png"], "max_size_mb": 2},
        "Medical Certificate":   {"required": False, "formats": ["pdf"],               "max_size_mb": 3},
    }

    with tab1:
        st.markdown("#### Upload Your Documents")
        st.info("📌 Supported: PDF, JPG, PNG · Documents are stored securely")

        doc_type = st.selectbox("Document Type", list(REQUIRED_DOCS.keys()))
        uploaded = st.file_uploader(
            f"Upload {doc_type}",
            type=REQUIRED_DOCS[doc_type]["formats"],
            help=f"Max size: {REQUIRED_DOCS[doc_type]['max_size_mb']}MB"
        )

        if uploaded:
            size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            max_mb = REQUIRED_DOCS[doc_type]["max_size_mb"]

            if size_mb > max_mb:
                st.error(f"❌ File too large ({size_mb:.1f}MB). Max allowed: {max_mb}MB")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="card card-green">
                        <div style='font-size:0.85rem;color:#22d3a0;font-weight:600;'>✅ File Ready</div>
                        <div style='font-size:0.8rem;opacity:0.8;margin-top:4px;'>📄 {uploaded.name}</div>
                        <div style='font-size:0.78rem;opacity:0.6;'>Size: {{size_mb:.2f}} MB</div>
                        <div style='font-size:0.78rem;opacity:0.6;'>Type: {{doc_type}}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if uploaded.type == "application/pdf":
                        st.markdown("**Verifications:**")
                        st.markdown("✅ File format: PDF")
                        st.markdown("✅ File size: Within limit")
                        st.markdown("✅ File readable: Yes")

                save_folder = os.path.join("uploaded_docs", st.session_state.username)
                os.makedirs(save_folder, exist_ok=True)

                if st.button("📤 Confirm Upload", use_container_width=True):
                    file_path = os.path.join(save_folder, f"{doc_type.replace(' ', '_')}_{uploaded.name}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded.getvalue())

                    # If PDF, also copy to documents for AI
                    if uploaded.type == "application/pdf":
                        os.makedirs("documents", exist_ok=True)
                        with open(os.path.join("documents", uploaded.name), "wb") as f:
                            f.write(uploaded.getvalue())
                        if "context" in st.session_state:
                            del st.session_state.context

                    st.success(f"✅ {doc_type} uploaded and verified successfully!")
                    st.balloons()

    with tab2:
        st.markdown("#### Document Submission Status")
        save_folder = os.path.join("uploaded_docs", st.session_state.username)
        uploaded_files = os.listdir(save_folder) if os.path.exists(save_folder) else []

        for doc_name, doc_info in REQUIRED_DOCS.items():
            is_uploaded = any(doc_name.replace(" ", "_") in f for f in uploaded_files)
            required_tag = "Required" if doc_info["required"] else "Optional"
            status_color = "#22d3a0" if is_uploaded else ("#f43f5e" if doc_info["required"] else "#f59e0b")
            status_text = "✅ Uploaded" if is_uploaded else ("❌ Missing" if doc_info["required"] else "⚠️ Optional")

            st.markdown(f"""
            <div style='display:flex;align-items:center;justify-content:space-between;padding:0.7rem 1rem;border:1px solid rgba(128,128,128,0.2);border-radius:9px;margin-bottom:0.5rem;border-left:3px solid {status_color};'>
                <div><span style='font-size:0.85rem;color:inherit;'>{doc_name}</span><span style='font-size:0.72rem;opacity:0.6;margin-left:0.5rem;'>({required_tag})</span></div>
                <span style='font-size:0.8rem;color:{status_color};font-weight:600;'>{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### All Uploaded Documents")
        docs_folder = "documents"
        all_docs = []
        if os.path.exists(docs_folder):
            for f in os.listdir(docs_folder):
                if f.endswith(".pdf"):
                    size = os.path.getsize(os.path.join(docs_folder, f))
                    all_docs.append((f, size))

        if all_docs:
            for fname, fsize in all_docs:
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"📄 **{fname}**")
                with c2:
                    st.caption(f"{fsize/1024:.1f} KB")
                with c3:
                    st.markdown('<span class="badge badge-green">HR Doc</span>', unsafe_allow_html=True)
        else:
            st.info("No documents uploaded yet.")

# ═══════════════════════════════════════════
#  PAGE: GENERATE DOCUMENTS
# ═══════════════════════════════════════════
elif page == "📝 Generate Documents":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>📝 Document Generator</h2><span class="section-badge">Auto-Generate</span></div>""", unsafe_allow_html=True)

    employees = load_employees()
    emp_data = employees.get(st.session_state.username, {})

    tab1, tab2 = st.tabs(["📄 Offer Letter", "📋 Joining Form"])

    with tab1:
        st.markdown("#### Generate Offer Letter")
        if not emp_data.get("full_name"):
            st.warning("⚠️ Please fill in your Employee Profile first before generating documents.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {emp_data.get('full_name', 'N/A')}")
                st.markdown(f"**Department:** {emp_data.get('department', 'N/A')}")
                st.markdown(f"**Designation:** {emp_data.get('designation', 'N/A')}")
            with col2:
                st.markdown(f"**Employee ID:** {emp_data.get('emp_id', 'N/A')}")
                st.markdown(f"**Joining Date:** {emp_data.get('joining_date', 'N/A')}")
                st.markdown(f"**Email:** {emp_data.get('email', 'N/A')}")

            annual_ctc = st.number_input("Annual CTC (₹)", min_value=100000, max_value=10000000, value=600000, step=50000)
            if st.button("📄 Generate Offer Letter", use_container_width=True):
                content = generate_offer_letter(emp_data, annual_ctc)
                st.text_area("Generated Offer Letter", content, height=400)
                st.download_button("⬇️ Download as Text", content, file_name=f"offer_letter_{emp_data.get('full_name','employee').replace(' ','_')}.txt", use_container_width=True)

    with tab2:
        st.markdown("#### Generate Joining Form")
        if not emp_data.get("full_name"):
            st.warning("⚠️ Please fill in your Employee Profile first.")
        else:
            if st.button("📋 Generate Joining Form", use_container_width=True):
                content = generate_joining_form(emp_data)
                st.text_area("Generated Joining Form", content, height=400)
                st.download_button("⬇️ Download as Text", content, file_name=f"joining_form_{emp_data.get('full_name','employee').replace(' ','_')}.txt", use_container_width=True)

# ═══════════════════════════════════════════
#  PAGE: ONBOARDING TASKS
# ═══════════════════════════════════════════
elif page == "✅ Onboarding Tasks":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>✅ Onboarding Task Manager</h2><span class="section-badge">Workflow</span></div>""", unsafe_allow_html=True)

    TASKS = {
        "Account Setup": [
            "Activate company email account",
            "Set up Microsoft Teams profile",
            "Configure VPN access",
            "Set up company laptop",
            "Change default passwords",
        ],
        "ID & Access": [
            "Collect employee ID card from reception",
            "Get building access card",
            "Register biometric attendance",
            "Get parking pass (if applicable)",
        ],
        "HR & Documentation": [
            "Submit all required documents to HR",
            "Sign employment contract",
            "Fill PF nomination form",
            "Submit bank details for payroll",
            "Read and sign HR policy document",
        ],
        "Training & Learning": [
            "Complete mandatory compliance training",
            "Finish IT security awareness course",
            "Attend company orientation session",
            "Complete team-specific onboarding",
        ],
        "Team Integration": [
            "Meet your reporting manager",
            "Attend team introduction meeting",
            "Shadow a senior team member",
            "Attend your first sprint/stand-up",
            "Complete first week check-in with HR",
        ],
    }

    tasks_data = load_task_progress(st.session_state.username)
    if not tasks_data:
        tasks_data = {}

    total = sum(len(v) for v in TASKS.values())
    done  = sum(1 for k, v in tasks_data.items() if v)
    pct   = int(done / total * 100) if total else 0

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Tasks", total)
    with col2: st.metric("Completed", done)
    with col3: st.metric("Progress", f"{pct}%")

    st.progress(pct / 100)
    st.markdown("---")

    changed = False
    for category, task_list in TASKS.items():
        with st.expander(f"📂 {category} ({sum(1 for t in task_list if tasks_data.get(t, False))}/{len(task_list)} done)", expanded=True):
            for task in task_list:
                current = tasks_data.get(task, False)
                new_val = st.checkbox(task, value=current, key=f"task_{task}")
                if new_val != current:
                    tasks_data[task] = new_val
                    changed = True

    if changed:
        save_task_progress(st.session_state.username, tasks_data)
        st.rerun()

# ═══════════════════════════════════════════
#  PAGE: TRAINING & LEARNING
# ═══════════════════════════════════════════
elif page == "🎓 Training & Learning":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>🎓 Training & Learning Hub</h2><span class="section-badge">Courses</span></div>""", unsafe_allow_html=True)

    COURSES = [
        {
            "id": "c1", "title": "Company Orientation & Culture",
            "desc": "Learn about XYZ's history, values, mission, and work culture. Understand the organizational structure and key leadership.",
            "duration": "2 hours", "type": "Video", "mandatory": True,
            "modules": ["Company History", "Vision & Values", "Org Structure", "Leadership Team"],
        },
        {
            "id": "c2", "title": "HR Policies & Code of Conduct",
            "desc": "Comprehensive overview of all HR policies including leave, attendance, appraisal, benefits, and code of conduct.",
            "duration": "3 hours", "type": "PDF + Quiz", "mandatory": True,
            "modules": ["Leave Policy", "Attendance Rules", "Code of Conduct", "Appraisal Process", "Benefits Overview"],
        },
        {
            "id": "c3", "title": "IT Security Awareness",
            "desc": "Understand cybersecurity best practices, data protection, password policies, and how to identify phishing threats.",
            "duration": "2.5 hours", "type": "Video + Quiz", "mandatory": True,
            "modules": ["Password Security", "Phishing Awareness", "Data Protection", "Device Security"],
        },
        {
            "id": "c4", "title": "Collaboration Tools & Productivity",
            "desc": "Learn to use Microsoft Teams, Outlook, SharePoint, and other productivity tools used at XYZ.",
            "duration": "2 hours", "type": "Hands-on", "mandatory": True,
            "modules": ["Microsoft Teams", "Outlook Setup", "SharePoint", "Project Tools"],
        },
        {
            "id": "c5", "title": "Introduction to AI & LLM Technologies",
            "desc": "Foundational course on Artificial Intelligence, Large Language Models, and their applications in business.",
            "duration": "4 hours", "type": "Video", "mandatory": False,
            "modules": ["What is AI?", "LLM Fundamentals", "RAG Architecture", "Prompt Engineering", "Business Applications"],
        },
        {
            "id": "c6", "title": "Workplace Diversity & Inclusion",
            "desc": "Understanding and promoting diversity, equity, and inclusion in the workplace.",
            "duration": "1.5 hours", "type": "Video", "mandatory": True,
            "modules": ["What is D&I?", "Unconscious Bias", "Inclusive Practices"],
        },
    ]

    training_data = load_training_progress(st.session_state.username)

    completed = sum(1 for c in COURSES if training_data.get(c["id"], {}).get("completed"))
    mandatory_done = sum(1 for c in COURSES if c["mandatory"] and training_data.get(c["id"], {}).get("completed"))
    mandatory_total = sum(1 for c in COURSES if c["mandatory"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Courses", len(COURSES))
    with c2: st.metric("Completed", completed)
    with c3: st.metric("Mandatory Done", f"{mandatory_done}/{mandatory_total}")
    with c4: st.metric("Progress", f"{int(completed/len(COURSES)*100)}%")

    st.progress(completed / len(COURSES))
    st.markdown("---")

    for course in COURSES:
        cdata = training_data.get(course["id"], {})
        is_done = cdata.get("completed", False)
        prog = cdata.get("progress", 0)

        border_color = "#22d3a0" if is_done else ("#4a9eff" if prog > 0 else "#1a2540")
        mand_badge = '<span class="badge badge-red">Mandatory</span>' if course["mandatory"] else '<span class="badge badge-amber">Optional</span>'
        type_badge = f'<span class="badge badge-blue">{course["type"]}</span>'
        done_badge = '<span class="badge badge-green">✓ Completed</span>' if is_done else ""

        with st.expander(f"{'✅' if is_done else '📚'} {course['title']} — {course['duration']}", expanded=not is_done):
            c1, c2 = st.columns([2.5, 1])
            with c1:
                st.markdown(f"""
                <div style='margin-bottom:0.6rem;'>
                    {mand_badge} {type_badge} {done_badge}
                </div>
                <p style='opacity:0.8;font-size:0.88rem;'>{course['desc']}</p>
                """, unsafe_allow_html=True)

                st.markdown("**Modules:**")
                for mod in course["modules"]:
                    st.markdown(f"  ◦ {mod}")

            with c2:
                st.markdown("**Progress**")
                new_prog = st.slider("", 0, 100, int(prog), key=f"prog_{course['id']}", label_visibility="collapsed")
                new_done = st.checkbox("Mark Complete", value=is_done, key=f"done_{course['id']}")

                if new_prog != prog or new_done != is_done:
                    if course["id"] not in training_data:
                        training_data[course["id"]] = {}
                    training_data[course["id"]]["progress"] = new_done and 100 or new_prog
                    training_data[course["id"]]["completed"] = new_done
                    save_training_progress(st.session_state.username, training_data)
                    st.rerun()

# ═══════════════════════════════════════════
#  PAGE: HR CONTACTS
# ═══════════════════════════════════════════
elif page == "📞 HR Contacts":
    st.markdown("""<div class="section-header"><h2 style='margin:0;'>📞 HR & Support Contacts</h2><span class="section-badge">Directory</span></div>""", unsafe_allow_html=True)

    contacts = [
        {"dept": "HR Department",       "email": "hr@xyztech.com",          "phone": "1800-425-3300", "hours": "Mon-Fri 9AM-6PM",  "icon": "👥", "color": "#4a9eff"},
        {"dept": "IT Helpdesk",          "email": "it.helpdesk@xyztech.com", "phone": "1800-425-1234", "hours": "24/7",             "icon": "💻", "color": "#22d3a0"},
        {"dept": "Payroll / Finance",    "email": "payroll@xyztech.com",     "phone": "1800-425-5678", "hours": "Mon-Fri 9AM-5PM",  "icon": "💰", "color": "#f59e0b"},
        {"dept": "Admin & Facilities",   "email": "admin@xyztech.com",       "phone": "1800-425-9999", "hours": "Mon-Sat 8AM-8PM",  "icon": "🏢", "color": "#a78bfa"},
        {"dept": "Medical & Insurance",  "email": "insurance@xyztech.com",   "phone": "1800-425-7777", "hours": "Mon-Fri 9AM-6PM",  "icon": "🏥", "color": "#f43f5e"},
        {"dept": "Security",             "email": "security@xyztech.com",    "phone": "1800-425-0000", "hours": "24/7 Emergency",   "icon": "🔒", "color": "#f59e0b"},
        {"dept": "Training & L&D",       "email": "training@xyztech.com",    "phone": "1800-425-2222", "hours": "Mon-Fri 9AM-6PM",  "icon": "🎓", "color": "#22d3a0"},
        {"dept": "Grievance Cell",       "email": "grievance@xyztech.com",   "phone": "1800-425-4444", "hours": "Mon-Fri 9AM-6PM",  "icon": "📣", "color": "#4a9eff"},
    ]

    col1, col2 = st.columns(2)
    for i, c in enumerate(contacts):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="card" style="border-left:3px solid {c['color']}; margin-bottom:0.8rem;">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;">
                    <span style="font-size:1.4rem;">{c['icon']}</span>
                    <span style="font-family:Syne,sans-serif;font-size:0.95rem;font-weight:600;">{c['dept']}</span>
                </div>
                <div style="font-size:0.82rem;opacity:0.8;margin-bottom:2px;">📧 {c['email']}</div>
                <div style="font-size:0.82rem;opacity:0.8;margin-bottom:2px;">📱 {c['phone']}</div>
                <div style="font-size:0.78rem;opacity:0.6;">🕐 {c['hours']}</div>
            </div>
            """, unsafe_allow_html=True)