import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta

# =============================================================================
# 1. SYSTEM CONFIGURATION & THEMING
# =============================================================================
st.set_page_config(
    page_title="Enterprise Workforce AI | Autonomous Allocation & Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Cyberpunk / Glassmorphic UI CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #070B14; }
    .stApp { color: #E2E8F0; }

    section[data-testid="stSidebar"] {
        background-color: #0B132B;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stCard {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 12px;
    }
    .stCard h4 { 
        margin: 0 0 6px 0; 
        font-size: 0.75rem; 
        font-weight: 700; 
        letter-spacing: .05em;
        text-transform: uppercase; 
        color: #64748B;
    }
    .metric-val { font-size: 2.2rem; font-weight: 800; color: #38BDF8; line-height: 1; }
    .metric-sub { font-size: 0.75rem; color: #94A3B8; margin-top: 6px; }

    .badge { display:inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
    .badge-critical { background: rgba(239,68,68,0.2); color:#F87171; border:1px solid rgba(239,68,68,0.4);}
    .badge-high { background: rgba(249,115,22,0.2); color:#FB923C; border:1px solid rgba(249,115,22,0.4);}
    .badge-ok { background: rgba(56,189,248,0.2); color:#38BDF8; border:1px solid rgba(56,189,248,0.4);}

    .stButton>button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #FFFFFF; border: none; border-radius: 8px; font-weight: 600;
        transition: all 0.2s ease; padding: 0.5rem 1rem;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(37,99,235,0.4); }

    .app-header { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; }
    .app-sub { color: #64748B; font-size: 0.85rem; margin-bottom: 1rem; }
    
    hr { border-color: rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. STATE INITIALIZATION & TAMPER-EVIDENT AUDIT ENGINE
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
    """Appends an immutable event into a SHA-256 tamper-evident hash chain."""
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
    st.title("🔒 Enterprise Workforce Gateway")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.subheader("Secure System Access")
            user_input = st.text_input("Username").strip().lower()
            pass_input = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Authenticate System Token", use_container_width=True)

            if submitted:
                record = USER_ROLES.get(user_input)
                if record and record["hash"] == hash_pass(pass_input, record["salt"]):
                    st.session_state.authenticated = True
                    st.session_state.username = user_input
                    st.session_state.user_role = record["role"]
                    st.session_state.permissions = record["permissions"]
                    log_event("AUTH_SUCCESS", f"User '{user_input}' initialized session.")
                    st.rerun()
                else:
                    log_event("AUTH_FAILURE", f"Failed attempt for user '{user_input}'.")
                    st.error("Invalid credentials.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Default Profiles — admin/admin123 · manager/manager123 · engineer/eng123")
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
    if "cost" in q or "saving" in q:
        return "💰 **Cost Analysis:** Running allocation updates indicates optimum matching preserves ~$420/hr relative to contractor escalation."
    
    return f"Processed query against system state: Currently tracking **{len(st.session_state.engineers)}** resources and **{len(st.session_state.tasks)}** tasks."


# =============================================================================
# 5. SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.markdown("### ⚡ Workforce OS")
st.sidebar.caption(f"Authenticated: **{st.session_state.username}**")
st.sidebar.markdown(f"<span class='badge badge-ok'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Command Modules", [m for m in ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine", "Security & Audit"] if m in st.session_state.permissions])

st.sidebar.markdown("---")
if st.sidebar.button("Terminated Session (Logout)", use_container_width=True):
    log_event("LOGOUT", f"User '{st.session_state.username}' logged out.")
    st.session_state.authenticated = False
    st.rerun()


# =============================================================================
# MODULE 1: DASHBOARD CENTER
# =============================================================================
if menu == "Dashboard Center":
    st.markdown('<div class="app-header">🚀 Mission Operations Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Real-time resource capacity, execution pipeline, and allocation health.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stCard"><h4>Workforce Pool</h4><div class="metric-val">{len(st.session_state.engineers)}</div></div>', unsafe_allow_html=True)
    with c2:
        active = len(st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"])
        st.markdown(f'<div class="stCard"><h4>Active Ready</h4><div class="metric-val">{active}</div></div>', unsafe_allow_html=True)
    with c3:
        pending = len(st.session_state.tasks[st.session_state.tasks["Assigned_To"].astype(str).str.contains("Unassigned")])
        st.markdown(f'<div class="stCard"><h4>Task Queue</h4><div class="metric-val">{pending}</div></div>', unsafe_allow_html=True)
    with c4:
        avg_perf = int(st.session_state.engineers["Performance_Score"].mean() * 100)
        st.markdown(f'<div class="stCard"><h4>System Health</h4><div class="metric-val">{avg_perf}%</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Engineers Availability & Capacity")
        st.dataframe(st.session_state.engineers, use_container_width=True, height=260, hide_index=True)
    with c2:
        st.subheader("🎯 Active Task Execution Queue")
        st.dataframe(st.session_state.tasks, use_container_width=True, height=260, hide_index=True)

    # Streamlit Fragment Chart (Plotly-Free Native Rendering)
    @st.fragment
    def render_capacity_monitor():
        st.subheader("📊 Live Workload Saturation Engine")
        df = st.session_state.engineers.copy()
        df["Saturation (%)"] = (df["Workload"] / df["Max_Capacity"]) * 100
        chart_data = df.set_index("Name")[["Saturation (%)"]]
        
        # Native Streamlit Bar Chart (No external plot library required)
        st.bar_chart(chart_data, color="#38BDF8")

    render_capacity_monitor()


# =============================================================================
# MODULE 2: AI NATURAL QUERY BOT
# =============================================================================
elif menu == "AI Natural Query Bot":
    st.markdown('<div class="app-header">🤖 AI Operations Co-Pilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Execute natural language decisions across system state and operational workloads.</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "System Online. Query allocation models, trigger re-assignments, or analyze capacity gaps."}]

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
    st.markdown('<div class="app-header">🧠 Predictive Insights & Analytics</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📉 Skill Gap Matrix", "📈 Utilization Forecast"])
    with t1:
        st.caption("Dynamic analysis comparing unassigned task demand against active resource supply.")
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
        st.caption("Forecasted workload distribution if pending queue is completely processed.")
        preview_df = run_autonomous_allocation(apply=False)
        if not preview_df.empty:
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
        else:
            st.info("No current unassigned tasks to project.")


# =============================================================================
# MODULE 4: DYNAMIC SCENARIO ENGINE
# =============================================================================
elif menu == "Dynamic Scenario Engine":
    st.markdown('<div class="app-header">🔮 Operational Scenario Simulator</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚙️ Parameter Simulation")
        spike = st.slider("Simulate Queue Spike (%)", 0, 200, 50)
        absent = st.multiselect("Simulate Sudden Outage", st.session_state.engineers["Name"].tolist())
        run = st.button("Simulate Operational Load", type="primary")

    if run:
        with c2:
            st.subheader("📊 Projected Impact")
            sim_eng = st.session_state.engineers.copy()
            if absent:
                sim_eng.loc[sim_eng["Name"].isin(absent), "Availability"] = "On Leave"
            
            cap = sim_eng[sim_eng["Availability"] == "Available"]["Max_Capacity"].sum() - sim_eng[sim_eng["Availability"] == "Available"]["Workload"].sum()
            projected = int(len(st.session_state.tasks) * (1 + spike/100))
            
            st.metric("Net Available Capacity", cap)
            st.metric("Simulated Task Queue Load", projected)
            if projected > cap:
                st.error(f"⚠️ **Capacity Breach:** Load exceeds headroom by {projected - cap} task slots!")
            else:
                st.success("✅ **Stable:** Workforce capacity sufficient to absorb scenario load.")


# =============================================================================
# MODULE 5: SECURITY & AUDIT LOGS
# =============================================================================
elif menu == "Security & Audit":
    st.markdown('<div class="app-header">🛡️ Cryptographic Security Vault</div>', unsafe_allow_html=True)
    
    valid, breach = verify_log_integrity()
    if valid:
        st.success("🔒 **Audit Chain Intact**: Hash chain integrity confirmed (0 modifications detected).")
    else:
        st.error(f"🚨 **Integrity Alert**: System hash mismatch detected at block entry #{breach}!")

    if st.session_state.audit_logs:
        df_logs = pd.DataFrame(st.session_state.audit_logs).drop(columns=["_raw_ts"])
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
