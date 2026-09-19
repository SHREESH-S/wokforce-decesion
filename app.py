import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI Workforce Allocation Agent",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------------------------------------------------
# INITIAL DATA SETUP (Session State for Dynamic Real-Time Updates)
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# ALLOCATION ENGINE (Scoring Mechanism)
# -----------------------------------------------------------------------------
def calculate_match_score(engineer, task):
    """
    Computes a match score based on skills, workload, urgency, SLA, location, and performance.
    """
    if engineer["Availability"] != "Available":
        return -1.0
    if engineer["Workload"] >= engineer["Max_Capacity"]:
        return -1.0
    
    score = 0.0
    
    # 1. Skill Match (Crucial)
    skills_list = [s.strip().lower() for s in engineer["Skills"].split(",")]
    if task["Required_Skill"].lower() in skills_list:
        score += 40.0
    else:
        return -1.0  # Hard constraint: Must have required skill
    
    # 2. Workload & Capacity Score
    capacity_ratio = 1.0 - (engineer["Workload"] / engineer["Max_Capacity"])
    score += capacity_ratio * 20.0
    
    # 3. Urgency & SLA Factor
    urgency_weights = {"Critical": 1.5, "High": 1.2, "Medium": 1.0, "Low": 0.8}
    urgency_multiplier = urgency_weights.get(task["Urgency"], 1.0)
    sla_factor = max(0, (24 - task["SLA_Hours"]) / 24.0)
    score += (sla_factor * 15.0) * urgency_multiplier
    
    # 4. Location Match
    if engineer["Location"].lower() == task["Location"].lower():
        score += 10.0
        
    # 5. Historical Performance
    score += engineer["Performance_Score"] * 15.0
    
    return score

def run_allocation_agent():
    """Dynamically matches unassigned tasks to the best available engineer."""
    eng_df = st.session_state.engineers.copy()
    task_df = st.session_state.tasks.copy()
    
    # Sort tasks by Urgency and SLA tightness
    urgency_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    task_df["urgency_rank"] = task_df["Urgency"].map(urgency_order)
    task_df = task_df.sort_values(by=["urgency_rank", "SLA_Hours"]).drop(columns=["urgency_rank"])
    
    allocations = []
    
    for _, task in task_df.iterrows():
        best_candidate = None
        best_score = -1.0
        
        for idx, engineer in eng_df.iterrows():
            score = calculate_match_score(engineer, task)
            if score > best_score:
                best_score = score
                best_candidate = idx
                
        if best_candidate is not None and best_score > 0:
            assigned_eng_id = eng_df.loc[best_candidate, "ID"]
            assigned_eng_name = eng_df.loc[best_candidate, "Name"]
            
            task_df.loc[task_df["Task_ID"] == task["Task_ID"], "Assigned_To"] = f"{assigned_eng_name} ({assigned_eng_id})"
            
            # Increment workload temporarily for allocation simulation
            eng_df.loc[best_candidate, "Workload"] += 1
            allocations.append({"Task": task["Task_Name"], "Assigned": assigned_eng_name, "Score": round(best_score, 2)})
        else:
            task_df.loc[task_df["Task_ID"] == task["Task_ID"], "Assigned_To"] = "Unassigned (No Suitable Match)"
            
    st.session_state.tasks = task_df

# -----------------------------------------------------------------------------
# USER INTERFACE
# -----------------------------------------------------------------------------
st.title("🤖 AI Workforce Decision & Resource Allocation Agent")
st.markdown("Dynamic real-time workforce allocation based on skills, workload, SLA, location, and performance.")

# Sidebar for Dynamic Control & Event Triggers
st.sidebar.header("⚡ Dynamic Event Trigger")
st.sidebar.markdown("Simulate changing conditions to force dynamic reallocation.")

# 1. Add New High Priority Task
with st.sidebar.expander("➕ Add High-Priority Task"):
    new_task_id = f"T{100 + len(st.session_state.tasks) + 1}"
    new_task_name = st.text_input("Task Name", f"Emergency Task {len(st.session_state.tasks)+1}")
    new_skill = st.selectbox("Required Skill", ["Python", "Cloud", "Security", "DevOps", "Database", "Network"])
    new_urgency = st.selectbox("Urgency", ["Critical", "High", "Medium", "Low"])
    new_sla = st.number_input("SLA (Hours)", min_value=1, max_value=48, value=2)
    new_loc = st.selectbox("Location", ["New York", "London", "Tokyo"])
    
    if st.button("Add Task"):
        new_row = pd.DataFrame([{
            "Task_ID": new_task_id, "Task_Name": new_task_name, "Required_Skill": new_skill,
            "Urgency": new_urgency, "SLA_Hours": new_sla, "Location": new_loc, "Assigned_To": "Unassigned"
        }])
        st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
        st.success(f"Task {new_task_id} added!")

# 2. Toggle Engineer Availability
with st.sidebar.expander("⚠️ Toggle Resource Availability"):
    eng_to_toggle = st.selectbox("Select Engineer", st.session_state.engineers["Name"].tolist())
    new_status = st.selectbox("Set Availability", ["Available", "On Leave", "Busy"])
    
    if st.button("Update Availability"):
        st.session_state.engineers.loc[st.session_state.engineers["Name"] == eng_to_toggle, "Availability"] = new_status
        st.warning(f"Updated status of {eng_to_toggle} to {new_status}")

# Run Optimization Button
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Run AI Re-allocation Engine", type="primary"):
    run_allocation_agent()
    st.sidebar.success("Allocation updated successfully!")

# Main Dashboard View
col1, col2 = st.columns(2)

with col1:
    st.subheader("👨‍💻 Workforce Status")
    st.dataframe(st.session_state.engineers, use_container_width=True)

with col2:
    st.subheader("📋 Task Queue & Assignments")
    st.dataframe(st.session_state.tasks, use_container_width=True)

# Visual Workload Chart
st.markdown("---")
st.subheader("📊 Engineer Capacity Utilization")
chart_df = st.session_state.engineers.copy()
chart_df["Capacity_Usage (%)"] = (chart_df["Workload"] / chart_df["Max_Capacity"]) * 100
st.bar_chart(chart_df.set_index("Name")["Capacity_Usage (%)"])
