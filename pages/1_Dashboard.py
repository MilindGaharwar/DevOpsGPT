import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import psutil

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("DevOps Agent Dashboard")

# Quick Actions Section
st.header("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Initialize New Project"):
        st.session_state['project_init'] = True
        st.success("Project initialization started!")

with col2:
    if st.button("Run Tests"):
        st.session_state['run_tests'] = True
        st.info("Running tests...")

with col3:
    if st.button("Deploy"):
        st.session_state['deploy'] = True
        st.info("Deployment started...")

# System Metrics
st.header("System Metrics")

# Create two columns for metrics
left_col, right_col = st.columns(2)

with left_col:
    # CPU Usage
    cpu_percent = psutil.cpu_percent()
    st.metric(
        label="CPU Usage",
        value=f"{cpu_percent}%",
        delta=f"{cpu_percent - 50:.1f}%" if cpu_percent > 50 else None,
    )

    # Memory Usage Chart
    memory = psutil.virtual_memory()
    memory_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=memory.percent,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Memory Usage"},
        gauge={'axis': {'range': [None, 100]},
               'steps': [
                   {'range': [0, 50], 'color': "lightgray"},
                   {'range': [50, 80], 'color': "gray"},
                   {'range': [80, 100], 'color': "red"}],
               'threshold': {
                   'line': {'color': "red", 'width': 4},
                   'thickness': 0.75,
                   'value': memory.percent}}))
    st.plotly_chart(memory_fig)

with right_col:
    # Disk Usage
    disk = psutil.disk_usage('/')
    st.metric(
        label="Disk Usage",
        value=f"{disk.percent}%",
        delta=f"{disk.free // (2**30)} GB free"
    )

    # Network Usage
    net_io = psutil.net_io_counters()
    network_fig = go.Figure()
    network_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=net_io.bytes_sent / 1024 / 1024,
        title={"text": "Network Out (MB)"},
        domain={'row': 0, 'column': 0}
    ))
    network_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=net_io.bytes_recv / 1024 / 1024,
        title={"text": "Network In (MB)"},
        domain={'row': 0, 'column': 1}
    ))
    network_fig.update_layout(
        grid={'rows': 1, 'columns': 2, 'pattern': "independent"},
        height=200
    )
    st.plotly_chart(network_fig)

# Recent Activity
st.header("Recent Activity")
if 'activities' not in st.session_state:
    st.session_state.activities = [
        {"timestamp": datetime.now() - timedelta(minutes=i), 
         "action": f"Sample activity {i+1}"} 
        for i in range(5)]

activities_df = pd.DataFrame(st.session_state.activities)
st.dataframe(activities_df, hide_index=True)
