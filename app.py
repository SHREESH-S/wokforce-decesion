import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime

# =============================================================================
# 1. SYSTEM CONFIGURATION & PREMIUM UI/UX THEME
# =============================================================================
st.set_page_config(
    page_title="Enterprise Workforce AI | Operational Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast Executive SaaS Theme
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #F8FAFC !important;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0B0F19 0%, #0F172A 100%);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }

    /* Premium Metric Card */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #38BDF8;
        line-height: 1;
    }

    /* Header Styling */
    .page-header {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .page-sub {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 24px;
    }

    /* Buttons */
    .stButton > button {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
    }
    .stButton > button:hover {
        background: #1D4ED8 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Login Form Card Container */
    .login-container {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 36px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .badge-admin { background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }

    /* Custom Form Field Inputs */
    .stTextInput input {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
    }
    .stTextInput input:focus {
        border-color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. STATE INITIALIZATION & AUDIT ENGINE
# =============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_baseline_data():
    engineers = pd.DataFrame([
        {"ID": "E1", "Name": "Alice Vance", "Skills": "Python, Cloud, Security", "Workload": 2, "Max_Capacity": 5, "Availability": "Available", "Location": "New York", "Performance_Score": 0.95, "Hourly_Rate": 85},
        {"ID": "E2", "Name": "Bob Smith", "Skills": "Python, DevOps, Cloud", "Workload": 3, "Max_Capacity": 5, "Availability": "Available", "Location": "London", "Performance_Score": 0.88, "Hourly_Rate": 75},
        {"ID": "E3", "Name": "Charlie Day", "Skills": "Security, Network", "Workload": 1, "Max_Capacity": 4, "Availability": "Available", "Location": "New York", "Performance_Score": 0.79, "Hourly_Rate": 65},
        {"ID": "E4", "Name": "Diana Prince", "Skills": "Cloud, DevOps, Database", "Workload": 0, "Max_Capacity": 5, "Availability": "Available", "Location": "Tokyo", "Performance_Score": 0.92, "Hourly_Rate": 90},
        {"ID": "E5", "Name": "Evan Wright", "Skills": "Python, Database", "Workload": 3, "Max_Capacity": 4, "Availability": "On Leave", "Location": "London", "Performance_Score": 0.85, "Hourly_Rate": 70},
        {"ID": "E6", "Name": "Farah Khan", "Skills": "Cloud, Security, Network", "Workload": 1, "Max_Capacity": 5, "Availability": "Available", "Location": "Berlin", "Performance_Score": 0.90, "Hourly_Rate": 80},
    ])

    tasks = pd.DataFrame([
        {"Task_ID": "T101", "Task_Name": "Database Migration", "Required_Skill": "Database", "Urgency": "High", "SLA_Hours": 4, "Location": "Tokyo", "Assigned_To": "Unassigned", "Est_Cost": 360},
        {"Task_ID": "T102", "Task_Name": "Cloud Security Audit", "Required_Skill": "Security", "Urgency": "Critical", "SLA_Hours": 2, "Location": "New York", "Assigned_To": "Unassigned", "Est_Cost": 170},
        {"Task_ID": "T103", "Task_Name": "API Optimization", "Required_Skill": "Python", "Urgency": "Medium", "SLA_Hours": 12, "Location": "London", "Assigned_To": "Unassigned", "Est_Cost": 900},
        {"Task_ID": "T104", "Task_Name": "CI/CD Pipeline Fix", "Required_Skill": "DevOps", "Urgency": "Low", "SLA_Hours": 24, "Location": "London", "Assigned_To": "Unassigned", "Est_Cost": 1800},
        {"Task_ID": "T105", "Task_Name": "Network Hardening", "Required_Skill": "Network", "Urgency": "Medium", "SLA_Hours": 10, "Location": "New York", "Assigned_To": "Unassigned", "Est_Cost": 650},
    ])
    return engineers, tasks

if "engineers" not in st.session_state or "tasks" not in st.session_state:
    st.session_state.engineers, st.session_state.tasks = load_baseline_data()

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

def log_event(event_type, details):
    prev_hash = st.session_state.audit_logs[-1]["Checksum"] if st.session_state.audit_logs else "GENESIS"
    timestamp = datetime.now().isoformat()
    raw_payload = f"{prev_hash}|{event_type}|{details}|{timestamp}"
    checksum = hashlib.sha256(raw_payload.encode()).hexdigest()[:16]
    
    st.session_state.audit_logs.append({
        "Timestamp": datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "Event": event_type,
        "Details": details,
        "Prev_Hash": prev_hash,
        "Checksum": checksum,
        "_raw_ts": timestamp
    })

def verify_log_integrity():
    prev = "GENESIS"
    for idx, log in enumerate(st.session_state.audit_logs):
        if log["Prev_Hash"] != prev:
            return False, idx
        payload = f"{log['Prev_Hash']}|{log['Event']}|{log['Details']}|{log['_raw_ts']}"
        expected = hashlib.sha256(payload.encode()).hexdigest()[:16]
        if expected != log["Checksum"]:
            return False, idx
        prev = log["Checksum"]
    return True, None


# =============================================================================
# 3. RBAC SECURITY GATEWAY
# =============================================================================
def hash_pass(password, salt):
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()

USER_ROLES = {
    "admin": {
        "salt": "s_adm_881", "hash": hash_pass("admin123", "s_adm_881"), "role": "Administrator",
        "permissions": ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine", "Security & Audit"]
    },
    "manager": {
        "salt": "s_mgr_412", "hash": hash_pass("manager123", "s_mgr_412"), "role": "Operations Manager",
        "permissions": ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine"]
    },
    "engineer": {
        "salt": "s_eng_990", "hash": hash_pass("eng123", "s_eng_990"), "role": "Engineer",
        "permissions": ["Dashboard Center", "AI Natural Query Bot"]
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write(" ")
    st.write(" ")
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown('''
            <div class="login-container">
                <h2 style="margin-top:0; font-weight:800; color:#F8FAFC; text-align:center;">Enterprise Workforce OS</h2>
                <p style="color:#94A3B8; font-size:0.9rem; text-align:center; margin-bottom:24px;">Sign in with your organizational credentials</p>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Username", placeholder="e.g. admin").strip().lower()
            pass_input = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In to Platform", use_container_width=True)

            if submitted:
                record = USER_ROLES.get(user_input)
                if record and record["hash"] == hash_pass(pass_input, record["salt"]):
                    st.session_state.authenticated = True
                    st.session_state.username = user_input
                    st.session_state.user_role = record["role"]
                    st.session_state.permissions = record["permissions"]
                    log_event("AUTH_SUCCESS", f"User '{user_input}' signed in.")
                    st.rerun()
                else:
                    log_event("AUTH_FAILURE", f"Failed login for '{user_input}'.")
                    st.error("Invalid username or password.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("<div style='text-align:center; margin-top:16px; color:#64748B;'>Default accounts: <b>admin</b>/admin123 · <b>manager</b>/manager123 · <b>engineer</b>/eng123</div>", unsafe_allow_html=True)
    st.stop()


# =============================================================================
# 4. ADVANCED MULTI-OBJECTIVE AI ALLOCATION ENGINE
# =============================================================================
def run_autonomous_allocation(apply=True):
    eng_df = st.session_state.engineers.copy()
    task_df = st.session_state.tasks.copy()

    urgency_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    task_df["priority"] = task_df["Urgency"].map(urgency_map) * 10 + (24 - task_df["SLA_Hours"])
    task_df = task_df.sort_values("priority", ascending=False)

    assigned_count = 0
    preview = []

    for idx, task in task_df.iterrows():
        if "Unassigned" in str(task["Assigned_To"]):
            req_skill = task["Required_Skill"].lower()
            candidates = []

            for e_idx, eng in eng_df.iterrows():
                if eng["Availability"] == "Available" and eng["Workload"] < eng["Max_Capacity"]:
                    skills = [s.strip().lower() for s in eng["Skills"].split(",")]
                    if req_skill in skills:
                        score = (
                            (eng["Performance_Score"] * 40)
                            + ((1.0 - (eng["Workload"] / eng["Max_Capacity"])) * 30)
                            + (30 if eng["Location"] == task["Location"] else 0)
                            - (eng["Hourly_Rate"] / 10.0)
                        )
                        candidates.append((score, e_idx, eng["Name"], eng["ID"]))

            if candidates:
                candidates.sort(reverse=True, key=lambda x: x[0])
                best = candidates[0]
                if apply:
                    task_df.loc[idx, "Assigned_To"] = f"{best[2]} ({best[3]})"
                    eng_df.loc[best[1], "Workload"] += 1
                else:
                    preview.append({"Task": task["Task_Name"], "Candidate": best[2], "Score": round(best[0], 2)})
                assigned_count += 1

    if apply:
        st.session_state.engineers = eng_df
        st.session_state.tasks = task_df.drop(columns=["priority"])
        log_event("AI_ALLOCATION", f"Autonomous engine reassigned {assigned_count} tasks.")
        return assigned_count
    return pd.DataFrame(preview)


def process_natural_query(query):
    q = query.lower()
    if "match" in q or "assign" in q or "allocate" in q:
        cnt = run_autonomous_allocation(apply=True)
        return f"⚡ **AI Allocation Complete:** Autonomous engine dynamically matched {cnt} unassigned tasks."
    if "gap" in q or "shortage" in q:
        tasks = st.session_state.tasks
        engineers = st.session_state.engineers
        unassigned = tasks[tasks["Assigned_To"].astype(str).str.contains("Unassigned")]
        
        skills = set(tasks["Required_Skill"])
        gaps = []
        for s in skills:
            d = (unassigned["Required_Skill"] == s).sum()
            avail = sum(1 for _, e in engineers.iterrows() if s.lower() in e["Skills"].lower() and e["Availability"] == "Available" and e["Workload"] < e["Max_Capacity"])
            if d > avail:
                gaps.append(f"**{s}** (Deficit: {d - avail})")
        return f"⚠️ **Skill Deficit Detected:** {', '.join(gaps)}" if gaps else "✅ **Skill Coverage Clear:** No immediate staffing deficits identified."
    
    return f"Processed query against system state: Currently tracking **{len(st.session_state.engineers)}** resources and **{len(st.session_state.tasks)}** tasks."


# =============================================================================
# 5. SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.markdown("<h3 style='margin-bottom:2px; font-weight:800; color:#F8FAFC;'>⚡ Workforce OS</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='margin-bottom:12px; color:#94A3B8; font-size:0.85rem;'>User: <b style='color:#F8FAFC;'>{st.session_state.username}</b></div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<span class='badge badge-admin'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color:#334155; margin:16px 0;'>", unsafe_allow_html=True)

menu = st.sidebar.radio("Main Menu", [m for m in ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine", "Security & Audit"] if m in st.session_state.permissions])

st.sidebar.markdown("<hr style='border-color:#334155; margin:24px 0;'>", unsafe_allow_html=True)
if st.sidebar.button("Sign Out", use_container_width=True):
    log_event("LOGOUT", f"User '{st.session_state.username}' signed out.")
    st.session_state.authenticated = False
    st.rerun()


# =============================================================================
# MODULE 1: DASHBOARD CENTER
# =============================================================================
if menu == "Dashboard Center":
    st.markdown('<div class="page-header">Mission Operations Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Real-time resource capacity, execution pipeline, and allocation health.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Workforce Pool</div><div class="metric-value">{len(st.session_state.engineers)}</div></div>', unsafe_allow_html=True)
    with c2:
        active = len(st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"])
        st.markdown(f'<div class="metric-card"><div class="metric-title">Active Engineers</div><div class="metric-value">{active}</div></div>', unsafe_allow_html=True)
    with c3:
        pending = len(st.session_state.tasks[st.session_state.tasks["Assigned_To"].astype(str).str.contains("Unassigned")])
        st.markdown(f'<div class="metric-card"><div class="metric-title">Unassigned Tasks</div><div class="metric-value">{pending}</div></div>', unsafe_allow_html=True)
    with c4:
        avg_perf = int(st.session_state.engineers["Performance_Score"].mean() * 100)
        st.markdown(f'<div class="metric-card"><div class="metric-title">System Health</div><div class="metric-value">{avg_perf}%</div></div>', unsafe_allow_html=True)

    st.write(" ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Engineers Availability & Capacity")
        st.dataframe(st.session_state.engineers, use_container_width=True, height=280, hide_index=True)
    with c2:
        st.subheader("🎯 Task Execution Queue")
        st.dataframe(st.session_state.tasks, use_container_width=True, height=280, hide_index=True)

    st.write(" ")
    st.subheader("📊 Live Workload Saturation")
    df = st.session_state.engineers.copy()
    df["Saturation (%)"] = (df["Workload"] / df["Max_Capacity"]) * 100
    chart_data = df.set_index("Name")[["Saturation (%)"]]
    st.bar_chart(chart_data, color="#38BDF8")


# =============================================================================
# MODULE 2: AI NATURAL QUERY BOT
# =============================================================================
elif menu == "AI Natural Query Bot":
    st.markdown('<div class="page-header">AI Operations Co-Pilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask questions and run allocation commands using natural language.</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am your AI assistant. Type **'Allocate unassigned tasks'** or **'Check skill gaps'** to get started."}]

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query = st.chat_input("Ex: 'Allocate unassigned tasks' or 'Check skill gaps'")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)
        response = process_natural_query(user_query)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)


# =============================================================================
# MODULE 3: AI INSIGHTS
# =============================================================================
elif menu == "AI Insights":
    st.markdown('<div class="page-header">Predictive Insights & Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Skill demand forecasting and automated workload projections.</div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["📉 Skill Gap Matrix", "📈 Utilization Forecast"])
    with t1:
        tasks = st.session_state.tasks
        engs = st.session_state.engineers
        unassigned = tasks[tasks["Assigned_To"].astype(str).str.contains("Unassigned")]
        
        matrix = []
        for skill in set(tasks["Required_Skill"]):
            demand = (unassigned["Required_Skill"] == skill).sum()
            supply = sum(1 for _, e in engs.iterrows() if skill.lower() in e["Skills"].lower() and e["Availability"] == "Available" and e["Workload"] < e["Max_Capacity"])
            matrix.append({"Skill": skill, "Demand (Tasks)": demand, "Supply (Engineers)": supply, "Status": "⚠️ Shortage" if demand > supply else "✅ Optimal"})
        st.dataframe(pd.DataFrame(matrix), use_container_width=True, hide_index=True)

    with t2:
        preview_df = run_autonomous_allocation(apply=False)
        if not preview_df.empty:
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
        else:
            st.info("No current unassigned tasks to project.")


# =============================================================================
# MODULE 4: DYNAMIC SCENARIO ENGINE
# =============================================================================
elif menu == "Dynamic Scenario Engine":
    st.markdown('<div class="page-header">Operational Scenario Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Simulate workload spikes and outages before making staffing changes.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚙️ Scenario Parameters")
        spike = st.slider("Simulate Queue Load Spike (%)", 0, 200, 50)
        absent = st.multiselect("Simulate Outages (Select Engineers)", st.session_state.engineers["Name"].tolist())
        run = st.button("Run Load Simulation", type="primary")

    if run:
        with c2:
            st.subheader("📊 Projected Impact")
            sim_eng = st.session_state.engineers.copy()
            if absent:
                sim_eng.loc[sim_eng["Name"].isin(absent), "Availability"] = "On Leave"
            
            cap = sim_eng[sim_eng["Availability"] == "Available"]["Max_Capacity"].sum() - sim_eng[sim_eng["Availability"] == "Available"]["Workload"].sum()
            projected = int(len(st.session_state.tasks) * (1 + spike/100))
            
            st.metric("Net Available Capacity", cap)
            st.metric("Simulated Queue Task Load", projected)
            if projected > cap:
                st.error(f"⚠️ **Capacity Breach:** Projected load exceeds available headroom by {projected - cap} task slots!")
            else:
                st.success("✅ **Stable:** System capacity can safely absorb the simulated load.")


# =============================================================================
# MODULE 5: SECURITY & AUDIT LOGS
# =============================================================================
elif menu == "Security & Audit":
    st.markdown('<div class="page-header">Cryptographic Security Vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">SHA-256 tamper-evident log verification.</div>', unsafe_allow_html=True)

    valid, breach = verify_log_integrity()
    if valid:
        st.success("🔒 **Audit Chain Intact:** All system log hashes verified successfully.")
    else:
        st.error(f"🚨 **Integrity Alert:** Modification detected at block entry #{breach}!")

    if st.session_state.audit_logs:
        df_logs = pd.DataFrame(st.session_state.audit_logs).drop(columns=["_raw_ts"])
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
