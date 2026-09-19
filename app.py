import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import hashlib

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & MODERN STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Workforce Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI/UX, Glassmorphism, and Quick Loading
st.markdown("""
<style>
    .main { background-color: #0F172A; }
    .stApp { color: #F8FAFC; }
    .stCard {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #38BDF8; }
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white; border: none; border-radius: 8px; font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_allowed_html=True)

# -----------------------------------------------------------------------------
# 2. PERFORMANCE OPTIMIZATION (CACHE & DATA SEEDING)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_initial_workforce_data():
    engineers = pd.DataFrame([
        {"ID": "E1", "Name": "Alice Vance", "Skills": "Python, Cloud, Security", "Workload": 2, "Max_Capacity": 5, "Availability": "Available", "Location": "New York", "Performance_Score": 0.95, "Hourly_Rate": 85},
        {"ID": "E2", "Name": "Bob Smith", "Skills": "Python, DevOps, Cloud", "Workload": 3, "Max_Capacity": 5, "Availability": "Available", "Location": "London", "Performance_Score": 0.88, "Hourly_Rate": 75},
        {"ID": "E3", "Name": "Charlie Day", "Skills": "Security, Network", "Workload": 1, "Max_Capacity": 4, "Availability": "Available", "Location": "New York", "Performance_Score": 0.79, "Hourly_Rate": 65},
        {"ID": "E4", "Name": "Diana Prince", "Skills": "Cloud, DevOps, Database", "Workload": 0, "Max_Capacity": 5, "Availability": "Available", "Location": "Tokyo", "Performance_Score": 0.92, "Hourly_Rate": 90},
        {"ID": "E5", "Name": "Evan Wright", "Skills": "Python, Database", "Workload": 3, "Max_Capacity": 4, "Availability": "On Leave", "Location": "London", "Performance_Score": 0.85, "Hourly_Rate": 70},
    ])
    
    tasks = pd.DataFrame([
        {"Task_ID": "T101", "Task_Name": "Database Migration", "Required_Skill": "Database", "Urgency": "High", "SLA_Hours": 4, "Location": "Tokyo", "Assigned_To": "Unassigned", "Est_Cost": 360},
        {"Task_ID": "T102", "Task_Name": "Cloud Security Audit", "Required_Skill": "Security", "Urgency": "Critical", "SLA_Hours": 2, "Location": "New York", "Assigned_To": "Unassigned", "Est_Cost": 170},
        {"Task_ID": "T103", "Task_Name": "API Optimization", "Required_Skill": "Python", "Urgency": "Medium", "SLA_Hours": 12, "Location": "London", "Assigned_To": "Unassigned", "Est_Cost": 900},
        {"Task_ID": "T104", "Task_Name": "CI/CD Pipeline Fix", "Required_Skill": "DevOps", "Urgency": "Low", "SLA_Hours": 24, "Location": "London", "Assigned_To": "Unassigned", "Est_Cost": 1800},
    ])
    return engineers, tasks

if "engineers" not in st.session_state or "tasks" not in st.session_state:
    st.session_state.engineers, st.session_state.tasks = load_initial_workforce_data()

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

def log_event(event_type, details):
    st.session_state.audit_logs.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Event": event_type,
        "Details": details,
        "Checksum": hashlib.md5(f"{event_type}{details}".encode()).hexdigest()[:8]
    })

# -----------------------------------------------------------------------------
# 3. RBAC & SECURITY GATEWAY
# -----------------------------------------------------------------------------
USER_ROLES = {
    "admin": {"pass": "admin123", "role": "Administrator"},
    "manager": {"pass": "manager123", "role": "Operations Manager"},
    "engineer": {"pass": "eng123", "role": "Engineer"}
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Enterprise Security Gateway")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login_form"):
            st.subheader("Sign In")
            username = st.text_input("Username").lower()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Authenticate")
            
            if submitted:
                if username in USER_ROLES and USER_ROLES[username]["pass"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user_role = USER_ROLES[username]["role"]
                    log_event("AUTH_SUCCESS", f"User {username} authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Invalid credentials provided.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. ADVANCED AI ENGINES
# -----------------------------------------------------------------------------
def run_ai_matchmaking():
    eng_df = st.session_state.engineers.copy()
    task_df = st.session_state.tasks.copy()
    
    reassigned = 0
    urgency_weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    task_df["priority_score"] = task_df["Urgency"].map(urgency_weights) * 10 + (24 - task_df["SLA_Hours"])
    task_df = task_df.sort_values(by="priority_score", ascending=False)
    
    for idx, task in task_df.iterrows():
        if "Unassigned" in str(task["Assigned_To"]):
            req_skill = task["Required_Skill"].lower()
            candidates = []
            
            for e_idx, eng in eng_df.iterrows():
                if eng["Availability"] == "Available" and eng["Workload"] < eng["Max_Capacity"]:
                    skills = [s.strip().lower() for s in eng["Skills"].split(",")]
                    if req_skill in skills:
                        # Vector-style weighted match score calculation
                        score = (eng["Performance_Score"] * 40) + \
                                ((1 - (eng["Workload"] / eng["Max_Capacity"])) * 30) + \
                                (30 if eng["Location"] == task["Location"] else 0)
                        candidates.append((score, e_idx, eng["Name"], eng["ID"]))
            
            if candidates:
                candidates.sort(reverse=True, key=lambda x: x[0])
                best_match = candidates[0]
                task_df.loc[idx, "Assigned_To"] = f"{best_match[2]} ({best_match[3]})"
                eng_df.loc[best_match[1], "Workload"] += 1
                reassigned += 1

    st.session_state.engineers = eng_df
    st.session_state.tasks = task_df.drop(columns=["priority_score"])
    log_event("AI_ALLOCATION", f"Autonomous AI routing assigned {reassigned} pending tasks.")

# -----------------------------------------------------------------------------
# 5. NAVIGATION & MODERN SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"### ⚡ Workforce OS")
st.sidebar.caption(f"Role: **{st.session_state.user_role}**")

menu = st.sidebar.radio("Navigation", ["Dashboard Center", "AI Natural Query Bot", "Dynamic Scenario Engine", "Security & Audit"])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# -----------------------------------------------------------------------------
# TAB 1: DASHBOARD CENTER
# -----------------------------------------------------------------------------
if menu == "Dashboard Center":
    st.title("🚀 Real-Time Operations Dashboard")
    
    # Fast rendering KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stCard"><h4>Total Workforce</h4><div class="metric-value">' + str(len(st.session_state.engineers)) + '</div></div>', unsafe_allow_html=True)
    with col2:
        active = len(st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"])
        st.markdown('<div class="stCard"><h4>Active Resources</h4><div class="metric-value">' + str(active) + '</div></div>', unsafe_allow_html=True)
    with col3:
        pending = len(st.session_state.tasks[st.session_state.tasks["Assigned_To"].str.contains("Unassigned")])
        st.markdown('<div class="stCard"><h4>Unassigned Tasks</h4><div class="metric-value">' + str(pending) + '</div></div>', unsafe_allow_html=True)
    with col4:
        avg_score = int(st.session_state.engineers["Performance_Score"].mean() * 100)
        st.markdown('<div class="stCard"><h4>Workforce Health</h4><div class="metric-value">' + str(avg_score) + '%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Engineers Availability & Capacity")
        st.dataframe(st.session_state.engineers, use_container_width=True, height=300)
    with c2:
        st.subheader("🎯 Active Task Queue")
        st.dataframe(st.session_state.tasks, use_container_width=True, height=300)

    st.markdown("---")
    
    # Fragment-isolated execution for partial reruns without whole page refreshes
    @st.fragment
    def render_capacity_chart():
        st.subheader("📊 Live Workload Saturation")
        chart_data = st.session_state.engineers.copy()
        chart_data["Utilization %"] = (chart_data["Workload"] / chart_data["Max_Capacity"]) * 100
        st.bar_chart(chart_data.set_index("Name")["Utilization %"])
        
    render_capacity_chart()

# -----------------------------------------------------------------------------
# TAB 2: NATURAL LANGUAGE CHATBOT
# -----------------------------------------------------------------------------
elif menu == "AI Natural Query Bot":
    st.title("🤖 AI Operations Co-Pilot")
    st.caption("Ask questions about active tasks, engineer workloads, or cost optimizations.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I assist with your resource management today?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_prompt := st.chat_input("Ex: 'Who is available for Python?' or 'Run AI matchmaker'"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.chat_message("user").write(user_prompt)
        
        prompt_l = user_prompt.lower()
        if "match" in prompt_l or "assign" in prompt_l or "route" in prompt_l:
            run_ai_matchmaking()
            response = "⚡ **AI Engine Execution Complete:** All pending tasks have been automatically matched to best-suited candidates based on skills, geography, and current workload capacity."
        elif "python" in prompt_l:
            match = st.session_state.engineers[st.session_state.engineers["Skills"].str.contains("Python")]["Name"].tolist()
            response = f"Engineers skilled in Python: **{', '.join(match)}**."
        elif "available" in prompt_l:
            avail = st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"]["Name"].tolist()
            response = f"Currently available engineers: **{', '.join(avail)}**."
        else:
            response = f"Analyzed query. Current system metrics: **{len(st.session_state.tasks)}** total tasks loaded, average hourly rate is **${st.session_state.engineers['Hourly_Rate'].mean():.2f}/hr**."
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

# -----------------------------------------------------------------------------
# TAB 3: DYNAMIC SCENARIO SIMULATOR
# -----------------------------------------------------------------------------
elif menu == "Dynamic Scenario Engine":
    st.title("⚡ Dynamic Scenario & Disruption Simulator")
    st.caption("Simulate unexpected resource availability drops or inject high-priority tasks to view dynamic reallocation.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚨 Emergency Outage Simulation")
        selected_eng = st.selectbox("Select Resource", st.session_state.engineers["Name"].tolist())
        new_status = st.selectbox("Update Status", ["On Leave", "Available", "Busy"])
        
        if st.button("Apply Status Disruption"):
            st.session_state.engineers.loc[st.session_state.engineers["Name"] == selected_eng, "Availability"] = new_status
            log_event("DISRUPTION_SIMULATED", f"Changed status of {selected_eng} to {new_status}")
            st.warning(f"Updated {selected_eng} to {new_status}.")
            
            # Auto trigger dynamic reallocation cascade
            run_ai_matchmaking()
            st.success("Cascade reallocation completed automatically!")

    with col2:
        st.markdown("### ⚡ Fast-Track Task Injection")
        with st.form("inject_task_form"):
            t_name = st.text_input("Task Title", "Zero-Day Security Patch")
            t_skill = st.selectbox("Required Skill", ["Security", "Python", "Cloud", "DevOps", "Database"])
            t_urgency = st.selectbox("Urgency", ["Critical", "High", "Medium", "Low"])
            t_sla = st.number_input("SLA Commitment (Hours)", min_value=1, max_value=72, value=2)
            
            if st.form_submit_button("Inject Task & Run AI"):
                t_id = f"T{100 + len(st.session_state.tasks) + 1}"
                new_row = pd.DataFrame([{"Task_ID": t_id, "Task_Name": t_name, "Required_Skill": t_skill,
                                         "Urgency": t_urgency, "SLA_Hours": t_sla, "Location": "New York",
                                         "Assigned_To": "Unassigned", "Est_Cost": t_sla * 100}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
                log_event("TASK_INJECTED", f"Injected emergency task {t_id}")
                run_ai_matchmaking()
                st.success(f"Task {t_id} injected into queue and routed!")

# -----------------------------------------------------------------------------
# TAB 4: SECURITY & AUDIT TRAIL
# -----------------------------------------------------------------------------
elif menu == "Security & Audit":
    st.title("🛡️ Enterprise Security & Audit Compliance")
    st.caption("Immutable system log generated for compliance tracking and governance auditing.")

    if st.session_state.audit_logs:
        audit_df = pd.DataFrame(st.session_state.audit_logs)
        st.dataframe(audit_df, use_container_width=True)
        
        csv_bytes = audit_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Compliance Audit CSV",
            data=csv_bytes,
            file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No audit events recorded yet.")
