import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# 1. PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="AI Workforce Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. GLOBAL STYLING — professional dark UI (loaded once, no inline CSS re-injection)
# =============================================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .main { background-color: #0B1120; }
    .stApp { color: #F1F5F9; }

    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .stCard {
        background: rgba(30, 41, 59, 0.55);
        border-radius: 14px;
        padding: 20px 22px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 24px -6px rgba(0,0,0,0.35);
        margin-bottom: 10px;
    }
    .stCard h4 { margin: 0 0 8px 0; font-size: 0.78rem; font-weight: 600; letter-spacing: .04em;
                 text-transform: uppercase; color: #94A3B8;}
    .metric-value { font-size: 2.1rem; font-weight: 800; color: #38BDF8; line-height: 1; }
    .metric-sub { font-size: 0.76rem; color: #64748B; margin-top: 6px; }

    .badge { display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; letter-spacing:.03em;}
    .badge-critical { background: rgba(239,68,68,0.15); color:#F87171; border:1px solid rgba(239,68,68,0.35);}
    .badge-high { background: rgba(249,115,22,0.15); color:#FB923C; border:1px solid rgba(249,115,22,0.35);}
    .badge-medium { background: rgba(234,179,8,0.15); color:#FACC15; border:1px solid rgba(234,179,8,0.35);}
    .badge-low { background: rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(34,197,94,0.35);}
    .badge-ok { background: rgba(56,189,248,0.15); color:#38BDF8; border:1px solid rgba(56,189,248,0.35);}
    .badge-danger { background: rgba(239,68,68,0.15); color:#F87171; border:1px solid rgba(239,68,68,0.35);}

    .stButton>button {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600;
        transition: all 0.2s ease; padding: 0.5rem 1rem;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(59,130,246,0.35); }

    .app-title { font-size: 1.55rem; font-weight: 800; margin-bottom: 0; }
    .app-sub { color: #64748B; font-size: 0.9rem; margin-top: 2px;}

    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    hr { border-color: rgba(255,255,255,0.08); }
</style>
""", unsafe_allow_html=True)


def badge(text, kind="ok"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def urgency_badge(urgency):
    mapping = {"Critical": "critical", "High": "high", "Medium": "medium", "Low": "low"}
    return badge(urgency, mapping.get(urgency, "ok"))


# =============================================================================
# 3. DATA LAYER — cached so cold start stays fast
# =============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_initial_workforce_data():
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
    st.session_state.engineers, st.session_state.tasks = load_initial_workforce_data()

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []


def log_event(event_type, details):
    """Append a tamper-evident, hash-chained audit entry (each entry commits to the previous one)."""
    prev_checksum = st.session_state.audit_logs[-1]["Checksum"] if st.session_state.audit_logs else "GENESIS"
    ts_raw = datetime.now().isoformat()
    payload = f"{prev_checksum}|{event_type}|{details}|{ts_raw}"
    checksum = hashlib.sha256(payload.encode()).hexdigest()[:16]
    st.session_state.audit_logs.append({
        "Timestamp": datetime.fromisoformat(ts_raw).strftime("%Y-%m-%d %H:%M:%S"),
        "Event": event_type,
        "Details": details,
        "Prev_Hash": prev_checksum,
        "Checksum": checksum,
        "_ts_raw": ts_raw,
    })


def verify_audit_chain():
    """Recompute the hash chain to confirm no log entry has been altered or removed."""
    logs = st.session_state.audit_logs
    prev = "GENESIS"
    for i, row in enumerate(logs):
        if row["Prev_Hash"] != prev:
            return False, i
        payload = f"{row['Prev_Hash']}|{row['Event']}|{row['Details']}|{row['_ts_raw']}"
        expected = hashlib.sha256(payload.encode()).hexdigest()[:16]
        if expected != row["Checksum"]:
            return False, i
        prev = row["Checksum"]
    return True, None


# =============================================================================
# 4. SECURITY GATEWAY — hashed credentials, lockout, RBAC, session expiry
# =============================================================================
def hash_pw(password, salt):
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()


USER_ROLES = {
    "admin": {
        "salt": "s_admin_9f2", "hash": hash_pw("admin123", "s_admin_9f2"),
        "role": "Administrator",
        "permissions": ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine", "Security & Audit"],
    },
    "manager": {
        "salt": "s_mgr_7c1", "hash": hash_pw("manager123", "s_mgr_7c1"),
        "role": "Operations Manager",
        "permissions": ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine"],
    },
    "engineer": {
        "salt": "s_eng_3a8", "hash": hash_pw("eng123", "s_eng_3a8"),
        "role": "Engineer",
        "permissions": ["Dashboard Center", "AI Natural Query Bot"],
    },
}

SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60

for key, default in [("authenticated", False), ("login_attempts", {})]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Session expiry check (runs before rendering anything else) ---
if st.session_state.authenticated:
    elapsed = datetime.now() - st.session_state.get("login_time", datetime.now())
    if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        log_event("SESSION_TIMEOUT", f"Session for {st.session_state.get('username','?')} expired after inactivity window.")
        st.session_state.authenticated = False
        st.warning("⏱️ Your session expired for security reasons. Please sign in again.")

if not st.session_state.authenticated:
    st.title("🔒 Enterprise Security Gateway")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.subheader("Sign In")
            username = st.text_input("Username").strip().lower()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Authenticate", use_container_width=True)

            if submitted:
                attempt_info = st.session_state.login_attempts.get(username, {"count": 0, "locked_until": None})

                if attempt_info["locked_until"] and datetime.now() < attempt_info["locked_until"]:
                    remaining = int((attempt_info["locked_until"] - datetime.now()).total_seconds())
                    st.error(f"🔒 Account temporarily locked. Try again in {remaining}s.")
                    log_event("AUTH_BLOCKED", f"Login blocked for '{username}' — account locked.")
                else:
                    record = USER_ROLES.get(username)
                    valid = record and record["hash"] == hash_pw(password, record["salt"])
                    if valid:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = record["role"]
                        st.session_state.permissions = record["permissions"]
                        st.session_state.login_time = datetime.now()
                        st.session_state.login_attempts[username] = {"count": 0, "locked_until": None}
                        log_event("AUTH_SUCCESS", f"User '{username}' authenticated successfully.")
                        st.rerun()
                    else:
                        count = attempt_info["count"] + 1
                        locked_until = datetime.now() + timedelta(seconds=LOCKOUT_SECONDS) if count >= MAX_LOGIN_ATTEMPTS else None
                        st.session_state.login_attempts[username] = {"count": count, "locked_until": locked_until}
                        log_event("AUTH_FAILURE", f"Failed login attempt #{count} for '{username}'.")
                        if locked_until:
                            st.error(f"🔒 Too many failed attempts. Account locked for {LOCKOUT_SECONDS}s.")
                        else:
                            st.error(f"Invalid credentials. ({count}/{MAX_LOGIN_ATTEMPTS} attempts)")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Demo accounts — admin / admin123 · manager / manager123 · engineer / eng123")
    st.stop()

# =============================================================================
# 5. AI ENGINES
# =============================================================================
def run_ai_matchmaking(apply=True):
    """Skill + geography + performance + cost aware assignment. apply=False returns a dry-run preview."""
    eng_df = st.session_state.engineers.copy()
    task_df = st.session_state.tasks.copy()

    urgency_weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    task_df["priority_score"] = task_df["Urgency"].map(urgency_weights) * 10 + (24 - task_df["SLA_Hours"])
    task_df = task_df.sort_values(by="priority_score", ascending=False)

    reassigned = 0
    preview_rows = []

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
                            + ((1 - (eng["Workload"] / eng["Max_Capacity"])) * 30)
                            + (30 if eng["Location"] == task["Location"] else 0)
                            - (eng["Hourly_Rate"] / 10.0)  # mild cost penalty as a tie-breaker
                        )
                        candidates.append((score, e_idx, eng["Name"], eng["ID"], eng["Hourly_Rate"]))

            if candidates:
                candidates.sort(reverse=True, key=lambda x: x[0])
                best = candidates[0]
                if apply:
                    task_df.loc[idx, "Assigned_To"] = f"{best[2]} ({best[3]})"
                    eng_df.loc[best[1], "Workload"] += 1
                else:
                    preview_rows.append({"Task_ID": task["Task_ID"], "Task_Name": task["Task_Name"],
                                          "Suggested_Engineer": best[2], "Match_Score": round(best[0], 1)})
                reassigned += 1

    if apply:
        st.session_state.engineers = eng_df
        st.session_state.tasks = task_df.drop(columns=["priority_score"])
        log_event("AI_ALLOCATION", f"Autonomous AI routing assigned {reassigned} pending task(s).")
        return reassigned
    else:
        return pd.DataFrame(preview_rows)


def compute_skill_gap_analysis():
    tasks = st.session_state.tasks
    engineers = st.session_state.engineers
    pending = tasks[tasks["Assigned_To"].astype(str).str.contains("Unassigned")]
    rows = []
    for skill in sorted(set(tasks["Required_Skill"])):
        demand = int((pending["Required_Skill"] == skill).sum())
        supply = 0
        for _, eng in engineers.iterrows():
            skills = [s.strip().lower() for s in eng["Skills"].split(",")]
            if skill.lower() in skills and eng["Availability"] == "Available" and eng["Workload"] < eng["Max_Capacity"]:
                supply += 1
        gap = demand - supply
        rows.append({"Skill": skill, "Pending_Demand": demand, "Available_Supply": supply,
                      "Status": "⚠️ Shortage" if gap > 0 else "✅ Covered"})
    return pd.DataFrame(rows)


def detect_workforce_anomalies():
    eng = st.session_state.engineers.copy()
    tasks = st.session_state.tasks
    eng["Utilization"] = eng["Workload"] / eng["Max_Capacity"]
    overloaded = eng[eng["Utilization"] >= 0.9]
    idle = eng[(eng["Workload"] == 0) & (eng["Availability"] == "Available")]
    sla_risk = tasks[(tasks["Assigned_To"].astype(str).str.contains("Unassigned")) & (tasks["Urgency"].isin(["Critical", "High"]))]
    return overloaded, idle, sla_risk


def generate_cost_optimization_suggestions(min_savings=5):
    eng = st.session_state.engineers
    tasks = st.session_state.tasks
    suggestions = []
    for _, task in tasks.iterrows():
        if "Unassigned" in str(task["Assigned_To"]):
            continue
        current_id = str(task["Assigned_To"]).split("(")[-1].replace(")", "").strip()
        current_row = eng[eng["ID"] == current_id]
        if current_row.empty:
            continue
        current_rate = current_row.iloc[0]["Hourly_Rate"]
        req_skill = task["Required_Skill"].lower()
        for _, cand in eng.iterrows():
            skills = [s.strip().lower() for s in cand["Skills"].split(",")]
            if (req_skill in skills and cand["ID"] != current_id and cand["Availability"] == "Available"
                    and cand["Workload"] < cand["Max_Capacity"] and cand["Hourly_Rate"] < current_rate - min_savings
                    and cand["Performance_Score"] >= 0.75):
                suggestions.append({
                    "Task_ID": task["Task_ID"], "Task_Name": task["Task_Name"],
                    "Current_Engineer": current_row.iloc[0]["Name"], "Current_Rate": current_rate,
                    "Suggested_Engineer": cand["Name"], "Suggested_Rate": cand["Hourly_Rate"],
                    "Est_Savings_Per_Hr": round(current_rate - cand["Hourly_Rate"], 2),
                })
                break
    return pd.DataFrame(suggestions)


def forecast_utilization():
    """Projects utilization if every currently pending task were routed right now (dry run, no mutation)."""
    preview = run_ai_matchmaking(apply=False)
    eng = st.session_state.engineers.copy()
    if not preview.empty:
        counts = preview["Suggested_Engineer"].value_counts()
        eng["Projected_Workload"] = eng.apply(
            lambda r: r["Workload"] + counts.get(r["Name"], 0), axis=1
        )
    else:
        eng["Projected_Workload"] = eng["Workload"]
    eng["Current_Util_%"] = (eng["Workload"] / eng["Max_Capacity"] * 100).round(1)
    eng["Projected_Util_%"] = np.clip(eng["Projected_Workload"] / eng["Max_Capacity"] * 100, 0, 150).round(1)
    return eng[["Name", "Current_Util_%", "Projected_Util_%"]], preview


# =============================================================================
# 6. CHATBOT INTENT ENGINE
# =============================================================================
KNOWN_SKILLS = ["python", "cloud", "security", "devops", "database", "network"]


def process_query(user_prompt):
    prompt_l = user_prompt.lower()

    if any(g in prompt_l for g in ["hello", "hi ", "hey"]) or prompt_l.strip() in ["hi", "hello", "hey"]:
        return "👋 Hello! I can run AI matchmaking, check availability, flag skill gaps, or suggest cost savings. Try 'run AI matcher' or 'skill gaps'."

    if any(k in prompt_l for k in ["match", "assign", "route"]):
        n = run_ai_matchmaking(apply=True)
        return f"⚡ **AI Engine Execution Complete:** {n} pending task(s) matched to best-suited candidates based on skills, geography, cost, and current workload capacity."

    if "gap" in prompt_l or "shortage" in prompt_l:
        gaps = compute_skill_gap_analysis()
        short = gaps[gaps["Status"].str.contains("Shortage")]
        if short.empty:
            return "✅ No skill shortages detected — supply currently covers all pending demand."
        rows = ", ".join(f"{r.Skill} ({r.Pending_Demand} pending vs {r.Available_Supply} available)" for r in short.itertuples())
        return f"⚠️ **Skill shortages detected:** {rows}."

    if "anomal" in prompt_l or "overload" in prompt_l or "risk" in prompt_l:
        overloaded, idle, sla_risk = detect_workforce_anomalies()
        parts = []
        if not overloaded.empty:
            parts.append(f"{len(overloaded)} engineer(s) at ≥90% utilization: {', '.join(overloaded['Name'])}")
        if not sla_risk.empty:
            parts.append(f"{len(sla_risk)} unassigned Critical/High task(s) at SLA risk: {', '.join(sla_risk['Task_ID'])}")
        if not idle.empty:
            parts.append(f"{len(idle)} idle available engineer(s): {', '.join(idle['Name'])}")
        return "🚨 " + " | ".join(parts) if parts else "✅ No workforce anomalies detected right now."

    if "cost" in prompt_l or "saving" in prompt_l or "cheaper" in prompt_l:
        sugg = generate_cost_optimization_suggestions()
        if sugg.empty:
            return "💰 No cost-saving reassignments found above the savings threshold."
        top = sugg.iloc[0]
        return (f"💰 **Top savings opportunity:** swap {top['Task_ID']} from {top['Current_Engineer']} "
                f"(${top['Current_Rate']}/hr) to {top['Suggested_Engineer']} (${top['Suggested_Rate']}/hr) "
                f"→ saves ${top['Est_Savings_Per_Hr']}/hr. {len(sugg)} total suggestion(s) available in AI Insights.")

    if "forecast" in prompt_l or "projection" in prompt_l or "utilization" in prompt_l:
        proj, _ = forecast_utilization()
        hottest = proj.sort_values("Projected_Util_%", ascending=False).iloc[0]
        return f"📈 If pending tasks were routed now, **{hottest['Name']}** would peak at {hottest['Projected_Util_%']}% utilization. Full breakdown is in AI Insights."

    matched_skill = next((s for s in KNOWN_SKILLS if s in prompt_l), None)
    if matched_skill:
        eng = st.session_state.engineers
        match = eng[eng["Skills"].str.lower().str.contains(matched_skill)]["Name"].tolist()
        return f"Engineers skilled in **{matched_skill.title()}**: {', '.join(match) if match else 'none found'}."

    if "available" in prompt_l:
        avail = st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"]["Name"].tolist()
        return f"Currently available engineers: **{', '.join(avail)}**."

    if "thank" in prompt_l:
        return "You're welcome! Let me know if you need another routing pass or a cost review."

    return (f"Analyzed query. Current system metrics: **{len(st.session_state.tasks)}** total tasks loaded, "
            f"average hourly rate **${st.session_state.engineers['Hourly_Rate'].mean():.2f}/hr**. "
            f"Try: 'skill gaps', 'anomalies', 'cost savings', or 'forecast'.")


# =============================================================================
# 7. SIDEBAR NAVIGATION (RBAC-filtered)
# =============================================================================
st.sidebar.markdown("### ⚡ Workforce OS")
st.sidebar.caption(f"Signed in as **{st.session_state.username}**")
st.sidebar.markdown(badge(st.session_state.user_role, "ok"), unsafe_allow_html=True)
st.sidebar.markdown("---")

ALL_MENU = ["Dashboard Center", "AI Natural Query Bot", "AI Insights", "Dynamic Scenario Engine", "Security & Audit"]
visible_menu = [m for m in ALL_MENU if m in st.session_state.permissions]
menu = st.sidebar.radio("Navigation", visible_menu)

st.sidebar.markdown("---")
if st.sidebar.button("Logout", use_container_width=True):
    log_event("LOGOUT", f"User '{st.session_state.username}' logged out.")
    st.session_state.authenticated = False
    st.rerun()

# =============================================================================
# TAB: DASHBOARD CENTER
# =============================================================================
if menu == "Dashboard Center":
    st.markdown('<p class="app-title">🚀 Real-Time Operations Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-sub">Live workforce capacity, task queue, and utilization at a glance.</p>', unsafe_allow_html=True)
    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stCard"><h4>Total Workforce</h4><div class="metric-value">{len(st.session_state.engineers)}</div></div>', unsafe_allow_html=True)
    with col2:
        active = len(st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"])
        st.markdown(f'<div class="stCard"><h4>Active Resources</h4><div class="metric-value">{active}</div></div>', unsafe_allow_html=True)
    with col3:
        pending = len(st.session_state.tasks[st.session_state.tasks["Assigned_To"].astype(str).str.contains("Unassigned")])
        st.markdown(f'<div class="stCard"><h4>Unassigned Tasks</h4><div class="metric-value">{pending}</div></div>', unsafe_allow_html=True)
    with col4:
        avg_score = int(st.session_state.engineers["Performance_Score"].mean() * 100)
        st.markdown(f'<div class="stCard"><h4>Workforce Health</h4><div class="metric-value">{avg_score}%</div></div>', unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Engineers Availability & Capacity")
        st.dataframe(st.session_state.engineers, use_container_width=True, height=280, hide_index=True)
    with c2:
        st.subheader("🎯 Active Task Queue")
        display_tasks = st.session_state.tasks.copy()
        st.dataframe(display_tasks, use_container_width=True, height=280, hide_index=True)

    st.markdown("---")

    @st.fragment
    def render_capacity_chart():
        st.subheader("📊 Live Workload Saturation")
        chart_data = st.session_state.engineers.copy()
        chart_data["Utilization %"] = (chart_data["Workload"] / chart_data["Max_Capacity"]) * 100
        fig = px.bar(chart_data, x="Name", y="Utilization %", color="Utilization %",
                     color_continuous_scale=["#22C55E", "#FACC15", "#EF4444"], range_color=[0, 100])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#F1F5F9", margin=dict(l=10, r=10, t=10, b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)

    render_capacity_chart()

    if st.session_state.user_role in ("Administrator", "Operations Manager"):
        with st.expander("➕ Add Engineer to Workforce Pool"):
            with st.form("add_engineer_form"):
                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    n_name = st.text_input("Full Name")
                    n_location = st.text_input("Location", "Remote")
                with ac2:
                    n_skills = st.multiselect("Skills", ["Python", "Cloud", "Security", "DevOps", "Database", "Network"])
                    n_capacity = st.number_input("Max Capacity", 1, 10, 5)
                with ac3:
                    n_rate = st.number_input("Hourly Rate ($)", 20, 500, 75)
                    n_perf = st.slider("Performance Score", 0.0, 1.0, 0.85)
                if st.form_submit_button("Add Engineer"):
                    if n_name and n_skills:
                        new_id = f"E{len(st.session_state.engineers) + 1}"
                        new_row = pd.DataFrame([{"ID": new_id, "Name": n_name, "Skills": ", ".join(n_skills),
                                                  "Workload": 0, "Max_Capacity": n_capacity, "Availability": "Available",
                                                  "Location": n_location, "Performance_Score": n_perf, "Hourly_Rate": n_rate}])
                        st.session_state.engineers = pd.concat([st.session_state.engineers, new_row], ignore_index=True)
                        log_event("ENGINEER_ADDED", f"Added engineer {n_name} ({new_id}) by {st.session_state.username}.")
                        st.success(f"Added {n_name} to the workforce pool.")
                    else:
                        st.error("Name and at least one skill are required.")

# =============================================================================
# TAB: AI NATURAL LANGUAGE CHATBOT
# =============================================================================
elif menu == "AI Natural Query Bot":
    st.markdown('<p class="app-title">🤖 AI Operations Co-Pilot</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-sub">Ask about tasks, workloads, skill gaps, anomalies, or cost optimization.</p>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I assist with your resource management today?"}]

    quick_prompts = ["Run AI matcher", "Any skill gaps?", "Show anomalies", "Cost savings?", "Forecast utilization"]
    qc = st.columns(len(quick_prompts))
    quick_click = None
    for i, qp in enumerate(quick_prompts):
        if qc[i].button(qp, use_container_width=True, key=f"quick_{i}"):
            quick_click = qp

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_prompt = st.chat_input("Ex: 'Who is available for Python?' or 'Run AI matchmaker'") or quick_click
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.chat_message("user").write(user_prompt)
        response = process_query(user_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

# =============================================================================
# TAB: AI INSIGHTS (skill gaps, anomalies, cost optimization, forecasting)
# =============================================================================
elif menu == "AI Insights":
    st.markdown('<p class="app-title">🧠 AI Insights & Recommendations</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-sub">Predictive and diagnostic AI models running on live workforce data.</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📉 Skill Gap Analysis", "🚨 Anomaly Detection", "💰 Cost Optimization", "📈 Utilization Forecast"])

    with tab1:
        st.caption("Compares pending task demand per skill against currently available, qualified supply.")
        gaps = compute_skill_gap_analysis()
        st.dataframe(gaps, use_container_width=True, hide_index=True)

    with tab2:
        st.caption("Flags overloaded engineers, idle capacity, and SLA-risk tasks still unassigned.")
        overloaded, idle, sla_risk = detect_workforce_anomalies()
        c1, c2, c3 = st.columns(3)
        c1.metric("Overloaded (≥90%)", len(overloaded))
        c2.metric("Idle & Available", len(idle))
        c3.metric("SLA-Risk Tasks", len(sla_risk))
        if not overloaded.empty:
            st.markdown("**Overloaded engineers**")
            st.dataframe(overloaded[["Name", "Workload", "Max_Capacity"]], use_container_width=True, hide_index=True)
        if not sla_risk.empty:
            st.markdown("**Unassigned Critical/High tasks at SLA risk**")
            st.dataframe(sla_risk[["Task_ID", "Task_Name", "Urgency", "SLA_Hours"]], use_container_width=True, hide_index=True)

    with tab3:
        st.caption("Suggests cheaper, equally-qualified engineers for currently assigned tasks (no auto-apply).")
        sugg = generate_cost_optimization_suggestions()
        if sugg.empty:
            st.info("No cost-saving reassignments found above the savings threshold.")
        else:
            st.dataframe(sugg, use_container_width=True, hide_index=True)
            st.caption(f"Total potential savings: ${sugg['Est_Savings_Per_Hr'].sum():.2f}/hr across {len(sugg)} task(s).")

    with tab4:
        st.caption("Dry-run projection of utilization if all pending tasks were routed right now — nothing is applied.")
        proj, preview = forecast_utilization()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Current %", x=proj["Name"], y=proj["Current_Util_%"], marker_color="#38BDF8"))
        fig.add_trace(go.Bar(name="Projected %", x=proj["Name"], y=proj["Projected_Util_%"], marker_color="#F97316"))
        fig.update_layout(barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#F1F5F9", margin=dict(l=10, r=10, t=10, b=10), height=340)
        st.plotly_chart(fig, use_container_width=True)
        if not preview.empty:
            st.dataframe(preview, use_container_width=True, hide_index=True)

# =============================================================================
# TAB: DYNAMIC SCENARIO SIMULATOR
# =============================================================================
elif menu == "Dynamic Scenario Engine":
    st.markdown('<p class="app-title">⚡ Dynamic Scenario & Disruption Simulator</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-sub">Simulate outages or inject high-priority tasks and watch AI reallocation cascade.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### 🚨 Emergency Outage Simulation")
        selected_eng = st.selectbox("Select Resource", st.session_state.engineers["Name"].tolist())
        new_status = st.selectbox("Update Status", ["On Leave", "Available", "Busy"])
        if st.button("Apply Status Disruption", use_container_width=True):
            st.session_state.engineers.loc[st.session_state.engineers["Name"] == selected_eng, "Availability"] = new_status
            log_event("DISRUPTION_SIMULATED", f"Changed status of {selected_eng} to {new_status} (by {st.session_state.username}).")
            st.warning(f"Updated {selected_eng} to {new_status}.")
            n = run_ai_matchmaking(apply=True)
            st.success(f"Cascade reallocation completed — {n} task(s) re-routed.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Fast-Track Task Injection")
        with st.form("inject_task_form"):
            t_name = st.text_input("Task Title", "Zero-Day Security Patch")
            t_skill = st.selectbox("Required Skill", ["Security", "Python", "Cloud", "DevOps", "Database", "Network"])
            t_urgency = st.selectbox("Urgency", ["Critical", "High", "Medium", "Low"])
            t_sla = st.number_input("SLA Commitment (Hours)", min_value=1, max_value=72, value=2)
            if st.form_submit_button("Inject Task & Run AI", use_container_width=True):
                t_id = f"T{100 + len(st.session_state.tasks) + 1}"
                new_row = pd.DataFrame([{"Task_ID": t_id, "Task_Name": t_name, "Required_Skill": t_skill,
                                          "Urgency": t_urgency, "SLA_Hours": t_sla, "Location": "New York",
                                          "Assigned_To": "Unassigned", "Est_Cost": t_sla * 100}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
                log_event("TASK_INJECTED", f"Injected emergency task {t_id} (by {st.session_state.username}).")
                n = run_ai_matchmaking(apply=True)
                st.success(f"Task {t_id} injected — {n} task(s) routed by AI.")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TAB: SECURITY & AUDIT TRAIL
# =============================================================================
elif menu == "Security & Audit":
    st.markdown('<p class="app-title">🛡️ Enterprise Security & Audit Compliance</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-sub">Hash-chained, tamper-evident log for compliance tracking and governance.</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🔍 Verify Chain Integrity", use_container_width=True):
            ok, bad_idx = verify_audit_chain()
            if ok:
                st.success("✅ Audit chain verified — no tampering detected.")
            else:
                st.error(f"⚠️ Integrity check failed at entry #{bad_idx}. Log may have been altered.")

    if st.session_state.audit_logs:
        audit_df = pd.DataFrame(st.session_state.audit_logs).drop(columns=["_ts_raw"])
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

        csv_bytes = audit_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Compliance Audit CSV",
            data=csv_bytes,
            file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No audit events recorded yet.")
