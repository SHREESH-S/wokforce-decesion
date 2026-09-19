import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Enterprise AI Workforce Allocation Platform",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------------------------------------------------------
# SECURITY & AUTHENTICATION (RBAC)
# -----------------------------------------------------------------------------
USER_ROLES = {
    "admin": {"pass": "admin123", "role": "Administrator"},
    "manager": {"pass": "manager123", "role": "Operations Manager"},
    "engineer": {"pass": "eng123", "role": "Engineer"}
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

def login():
    st.sidebar.title("🔒 Security Gateway")
    username = st.sidebar.text_input("Username").lower()
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in USER_ROLES and USER_ROLES[username]["pass"] == password:
            st.session_state.authenticated = True
            st.session_state.user_role = USER_ROLES[username]["role"]
            st.sidebar.success(f"Logged in as {USER_ROLES[username]['role']}")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials.")

if not st.session_state.authenticated:
    st.title("🔒 Enterprise AI Workforce Platform")
    st.info("Please log in using the sidebar to access allocation agents and security controls.")
    login()
    st.stop()

# -----------------------------------------------------------------------------
# INITIAL DATA & STATE SETUP
# -----------------------------------------------------------------------------
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

def log_event(event_type, description):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_logs.append({"Timestamp": timestamp, "Type": event_type, "Details": description})

if "engineers" not in st.session_state:
    st.session_state.engineers = pd.DataFrame([
        {"ID": "E1", "Name": "Alice Vance", "Skills": "Python, Cloud, Security", "Workload": 2, "Max_Capacity": 5, "Availability": "Available", "Location": "New York", "Performance_Score": 0.95},
        {"ID": "E2", "Name": "Bob Smith", "Skills": "Python, DevOps, Cloud", "Workload": 4, "Max_Capacity": 5, "Availability": "Available", "Location": "London", "Performance_Score": 0.88},
        {"ID": "E3", "Name": "Charlie Day", "Skills": "Security, Network", "Workload": 1, "Max_Capacity": 4, "Availability": "Available", "Location": "New York", "Performance_Score": 0.79},
        {"ID": "E4", "Name": "Diana Prince", "Skills": "Cloud, DevOps, Database", "Workload": 0, "Max_Capacity": 5, "Availability": "Available", "Location": "Tokyo", "Performance_Score": 0.92},
        {"ID": "E5", "Name": "Evan Wright", "Skills": "Python, Database", "Workload": 3, "Max_Capacity": 4, "Availability": "On Leave", "Location": "London", "Performance_Score": 0.85},
    ])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame([
        {"Task_ID": "T101", "Task_Name": "Database Migration", "Required_Skill": "Database", "Urgency": "High", "SLA_Hours": 4, "Location": "Tokyo", "Assigned_To": "Unassigned"},
        {"Task_ID": "T102", "Task_Name": "Cloud Security Audit", "Required_Skill": "Security", "Urgency": "Critical", "SLA_Hours": 2, "Location": "New York", "Assigned_To": "Unassigned"},
        {"Task_ID": "T103", "Task_Name": "API Optimization", "Required_Skill": "Python", "Urgency": "Medium", "SLA_Hours": 12, "Location": "London", "Assigned_To": "Unassigned"},
        {"Task_ID": "T104", "Task_Name": "CI/CD Pipeline Fix", "Required_Skill": "DevOps", "Urgency": "Low", "SLA_Hours": 24, "Location": "London", "Assigned_To": "Unassigned"},
    ])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Workforce Operations Assistant. Ask me about workforce capacity, active tasks, or allocation optimization."}
    ]

# -----------------------------------------------------------------------------
# ADVANCED MULTI-FACTOR DECISION ENGINE
# -----------------------------------------------------------------------------
def calculate_match_score(engineer, task):
    if engineer["Availability"] != "Available" or engineer["Workload"] >= engineer["Max_Capacity"]:
        return -1.0
    
    score = 0.0
    skills_list = [s.strip().lower() for s in engineer["Skills"].split(",")]
    
    # 1. Mandatory Skill Verification
    if task["Required_Skill"].lower() not in skills_list:
        return -1.0
    score += 40.0
    
    # 2. Capacity Utilization Score
    score += (1.0 - (engineer["Workload"] / engineer["Max_Capacity"])) * 20.0
    
    # 3. Dynamic SLA and Urgency Weighting
    urgency_weights = {"Critical": 1.6, "High": 1.3, "Medium": 1.0, "Low": 0.7}
    sla_urgency_bonus = max(0, (24 - task["SLA_Hours"]) / 24.0) * 15.0 * urgency_weights.get(task["Urgency"], 1.0)
    score += sla_urgency_bonus
    
    # 4. Proximity & Location Weighting
    if engineer["Location"].lower() == task["Location"].lower():
        score += 10.0
        
    # 5. Historical Reliability Index
    score += engineer["Performance_Score"] * 15.0
    return score

def execute_auto_allocation():
    eng_df = st.session_state.engineers.copy()
    task_df = st.session_state.tasks.copy()
    
    urgency_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    task_df["rank"] = task_df["Urgency"].map(urgency_order)
    task_df = task_df.sort_values(by=["rank", "SLA_Hours"]).drop(columns=["rank"])
    
    reassignments = 0
    for _, task in task_df.iterrows():
        best_candidate, best_score = None, -1.0
        for idx, engineer in eng_df.iterrows():
            score = calculate_match_score(engineer, task)
            if score > best_score:
                best_score, best_candidate = score, idx
                
        if best_candidate is not None and best_score > 0:
            assigned_name = eng_df.loc[best_candidate, "Name"]
            assigned_id = eng_df.loc[best_candidate, "ID"]
            task_df.loc[task_df["Task_ID"] == task["Task_ID"], "Assigned_To"] = f"{assigned_name} ({assigned_id})"
            eng_df.loc[best_candidate, "Workload"] += 1
            reassignments += 1
        else:
            task_df.loc[task_df["Task_ID"] == task["Task_ID"], "Assigned_To"] = "Unassigned (No Match)"
            
    st.session_state.tasks = task_df
    log_event("ALLOCATION_ENGINE", f"Automated reallocation complete. {reassignments} tasks routed.")

# -----------------------------------------------------------------------------
# NAVIGATION & HEADER
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"**User:** {st.session_state.user_role}")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.title("⚡ AI Workforce Decision & Resource Allocation Platform")
menu = st.sidebar.radio("Navigation", ["Dashboard & Control", "AI Operations Chatbot", "Automation Triggers", "Security Audit Logs"])

# -----------------------------------------------------------------------------
# TAB 1: DASHBOARD & CONTROL
# -----------------------------------------------------------------------------
if menu == "Dashboard & Control":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Engineers", len(st.session_state.engineers))
    col2.metric("Available Pool", len(st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"]))
    col3.metric("Total Tasks", len(st.session_state.tasks))
    col4.metric("Unassigned Tasks", len(st.session_state.tasks[st.session_state.tasks["Assigned_To"].str.contains("Unassigned")]))

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("👨‍💻 Real-Time Engineer Capacity")
        st.dataframe(st.session_state.engineers, use_container_width=True)
        
    with c2:
        st.subheader("📋 Task Routing & Queue")
        st.dataframe(st.session_state.tasks, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Load Balancing Analytics")
    
    chart_df = st.session_state.engineers.copy()
    chart_df["Capacity Utilization (%)"] = (chart_df["Workload"] / chart_df["Max_Capacity"]) * 100
    fig = px.bar(chart_df, x="Name", y="Capacity Utilization (%)", color="Availability", 
                 title="Workload Saturation per Engineer", range_y=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: AI CHATBOT ASSISTANT
# -----------------------------------------------------------------------------
elif menu == "AI Operations Chatbot":
    st.subheader("💬 AI Resource Optimization Chatbot")
    st.markdown("Query the active workforce database in natural language.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question (e.g., 'Who is available for Python tasks?'):"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        p_lower = prompt.lower()
        if "available" in p_lower:
            avail = st.session_state.engineers[st.session_state.engineers["Availability"] == "Available"]["Name"].tolist()
            response = f"Currently available engineers: **{', '.join(avail)}**."
        elif "unassigned" in p_lower:
            unassigned = st.session_state.tasks[st.session_state.tasks["Assigned_To"].str.contains("Unassigned")]["Task_Name"].tolist()
            response = f"Unassigned tasks in queue: **{', '.join(unassigned) if unassigned else 'None'}**."
        elif "python" in p_lower:
            py_eng = st.session_state.engineers[st.session_state.engineers["Skills"].str.contains("Python")]["Name"].tolist()
            response = f"Engineers skilled in Python: **{', '.join(py_eng)}**."
        else:
            response = "I can analyze active tasks, workforce availability, and skill matching. Try asking: 'Who is available?' or 'Which tasks are unassigned?'"

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# -----------------------------------------------------------------------------
# TAB 3: AUTOMATION TRIGGERS
# -----------------------------------------------------------------------------
elif menu == "Automation Triggers":
    st.subheader("⚡ Automated Dynamic Event Triggers")
    st.markdown("Simulate continuous changes in conditions to trigger immediate AI reallocation.")

    if st.session_state.user_role == "Engineer":
        st.warning("🔒 Access Restricted: Engineer level accounts cannot trigger system-wide reallocations.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ➕ Dynamic Task Injection")
            t_name = st.text_input("Task Title", "SLA Breach Mitigation")
            t_skill = st.selectbox("Required Skill", ["Python", "Cloud", "Security", "DevOps", "Database"])
            t_urgency = st.selectbox("Urgency", ["Critical", "High", "Medium", "Low"])
            t_sla = st.slider("SLA Window (Hours)", 1, 48, 2)
            t_loc = st.selectbox("Location Target", ["New York", "London", "Tokyo"])
            
            if st.button("Inject Task & Trigger Auto-Allocation"):
                t_id = f"T{100 + len(st.session_state.tasks) + 1}"
                new_task = pd.DataFrame([{"Task_ID": t_id, "Task_Name": t_name, "Required_Skill": t_skill, 
                                          "Urgency": t_urgency, "SLA_Hours": t_sla, "Location": t_loc, "Assigned_To": "Unassigned"}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                log_event("TASK_INJECTION", f"New task {t_id} injected into queue.")
                execute_auto_allocation()
                st.success("Task injected and auto-allocation executed!")

        with col2:
            st.markdown("### ⚠️ Dynamic Capacity Disturbance")
            target_eng = st.selectbox("Select Target Engineer", st.session_state.engineers["Name"].tolist())
            new_status = st.selectbox("Update Availability State", ["Available", "On Leave", "Busy"])
            
            if st.button("Apply Status Change & Re-balance"):
                st.session_state.engineers.loc[st.session_state.engineers["Name"] == target_eng, "Availability"] = new_status
                log_event("AVAILABILITY_CHANGE", f"Status of {target_eng} changed to {new_status}.")
                execute_auto_allocation()
                st.warning("Resource status changed and system re-balanced!")

# -----------------------------------------------------------------------------
# TAB 4: SECURITY AUDIT LOGS
# -----------------------------------------------------------------------------
elif menu == "Security Audit Logs":
    st.subheader("🛡️ Enterprise Audit & Event Logs")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("No system events recorded in this session yet.")
