import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="AI Workforce Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "engineers" not in st.session_state or "tasks" not in st.session_state:
    st.session_state.engineers = pd.DataFrame([
        {"ID": "E1", "Name": "Alice Vance", "Skills": "Python, Cloud", "Workload": 2, "Max_Capacity": 5, "Availability": "Available", "Location": "New York", "Performance_Score": 0.95, "Hourly_Rate": 85},
        {"ID": "E2", "Name": "Bob Smith", "Skills": "DevOps, Cloud", "Workload": 3, "Max_Capacity": 5, "Availability": "Available", "Location": "London", "Performance_Score": 0.88, "Hourly_Rate": 75},
        {"ID": "E3", "Name": "Charlie Day", "Skills": "Security, Network", "Workload": 1, "Max_Capacity": 4, "Availability": "Available", "Location": "New York", "Performance_Score": 0.79, "Hourly_Rate": 65},
    ])
    st.session_state.tasks = pd.DataFrame([
        {"Task_ID": "T101", "Task_Name": "Database Migration", "Required_Skill": "Cloud", "Urgency": "High", "SLA_Hours": 4, "Assigned_To": "Unassigned"},
        {"Task_ID": "T102", "Task_Name": "Security Audit", "Required_Skill": "Security", "Urgency": "Critical", "SLA_Hours": 2, "Assigned_To": "Unassigned"},
    ])

# =============================================================================
# DASHBOARD LAYOUT
# =============================================================================
st.title("⚡ AI Workforce Command Center")

col1, col2, col3 = st.columns(3)
col1.metric("Total Engineers", len(st.session_state.engineers))
col2.metric("Pending Tasks", len(st.session_state.tasks[st.session_state.tasks["Assigned_To"] == "Unassigned"]))
col3.metric("Avg Performance", f"{int(st.session_state.engineers['Performance_Score'].mean() * 100)}%")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.subheader("👥 Engineers")
    st.dataframe(st.session_state.engineers, use_container_width=True, hide_index=True)

with c2:
    st.subheader("🎯 Tasks")
    st.dataframe(st.session_state.tasks, use_container_width=True, hide_index=True)

# Performance-Optimized Chart Fragment
@st.fragment
def render_chart():
    st.subheader("📊 Workload Saturation")
    df = st.session_state.engineers.copy()
    df["Utilization %"] = (df["Workload"] / df["Max_Capacity"]) * 100
    fig = px.bar(df, x="Name", y="Utilization %", color="Utilization %",
                 color_continuous_scale=["#22C55E", "#FACC15", "#EF4444"])
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

render_chart()
