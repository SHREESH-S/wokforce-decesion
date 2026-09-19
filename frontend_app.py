import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuration
st.set_page_config(page_title="AI Workforce Command Center", page_icon="⚡", layout="wide")
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Helper Functions
def api_get(endpoint):
    try:
        res = requests.get(f"{BACKEND_URL}/{endpoint}", timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

def api_post(endpoint, payload):
    try:
        res = requests.post(f"{BACKEND_URL}/{endpoint}", json=payload, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

# Load Initial API Data
engineers_data = api_get("engineers")
tasks_data = api_get("tasks")
telemetry_data = api_get("telemetry")

# Session State Setup
if "engineers" not in st.session_state or engineers_data:
    st.session_state.engineers = pd.DataFrame(engineers_data if engineers_data else [
        {"id": "E101", "name": "Alice Vance", "skills": ["Python", "Cloud"], "workload": 2, "max_capacity": 5, "location": "New York", "performance_score": 0.95, "hourly_rate": 85.0},
        {"id": "E102", "name": "Bob Smith", "skills": ["DevOps", "Cloud"], "workload": 4, "max_capacity": 5, "location": "London", "performance_score": 0.88, "hourly_rate": 75.0},
    ])

if "tasks" not in st.session_state or tasks_data:
    st.session_state.tasks = pd.DataFrame(tasks_data if tasks_data else [
        {"task_id": "T201", "task_name": "Cloud Migration", "required_skill": "Cloud", "urgency": "Critical", "sla_hours": 3, "location": "New York", "assigned_to": "Unassigned"},
    ])

# UI Header
st.title("⚡ AI Workforce Command Center")
st.caption("Decoupled System Architecture | Streamlit Frontend + FastAPI Backend")

# Telemetry Banner
if telemetry_data:
    if telemetry_data["health_status"] == "Warning":
        st.warning(f"⚠️ **Telemetry Alert**: Overcapacity Risk ({len(telemetry_data['burnout_risk_warnings'])}) | SLA Risks ({len(telemetry_data['sla_breach_risks'])})")

# Metric Bar
c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Resources", len(st.session_state.engineers))
c2.metric("Unassigned Tasks", len(st.session_state.tasks[st.session_state.tasks["assigned_to"] == "Unassigned"]))
c3.metric("Avg Capacity Saturation", f"{int((st.session_state.engineers['workload'].sum() / st.session_state.engineers['max_capacity'].sum()) * 100)}%")
c4.metric("Backend Server", "Connected" if engineers_data else "Offline")

st.markdown("---")

# Action Bar
st.subheader("🤖 Optimization Control")
if st.button("Run Algorithmic Matchmaker", type="primary"):
    payload = {
        "engineers": st.session_state.engineers.to_dict(orient="records"),
        "tasks": st.session_state.tasks.to_dict(orient="records")
    }
    result = api_post("optimize", payload)
    
    if result:
        st.success(f"Matched {result['total_assigned']} tasks via FastAPI engine!")
        st.json(result["assignments"])
    else:
        st.error("Could not execute optimization. Backend server unreachable.")

# Data Tables
col1, col2 = st.columns(2)
with col1:
    st.subheader("👥 Engineers Pool")
    st.dataframe(st.session_state.engineers, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🎯 Active Task Queue")
    st.dataframe(st.session_state.tasks, use_container_width=True, hide_index=True)

# Saturation Visualization
st.subheader("📊 Resource Saturation Levels")
chart_df = st.session_state.engineers.copy()
chart_df["Utilization_%"] = (chart_df["workload"] / chart_df["max_capacity"]) * 100

fig = px.bar(
    chart_df,
    x="name",
    y="Utilization_%",
    color="Utilization_%",
    color_continuous_scale=["#22c55e", "#eab308", "#ef4444"],
    range_y=[0, 100]
)
fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)
