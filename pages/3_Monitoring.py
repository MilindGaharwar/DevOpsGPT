import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import psutil
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Monitoring", page_icon="📈", layout="wide")

st.title("System Monitoring")

# Initialize metrics history if not exists
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# Function to get current metrics
def get_current_metrics():
    return {
        'timestamp': datetime.now(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'network_sent': psutil.net_io_counters().bytes_sent / 1024 / 1024,  # MB
        'network_recv': psutil.net_io_counters().bytes_recv / 1024 / 1024   # MB
    }

# Update metrics every second
current_metrics = get_current_metrics()
st.session_state.metrics_history.append(current_metrics)

# Keep only last hour of data
one_hour_ago = datetime.now() - timedelta(hours=1)
st.session_state.metrics_history = [
    m for m in st.session_state.metrics_history 
    if m['timestamp'] > one_hour_ago
]

# Convert metrics history to DataFrame
df = pd.DataFrame(st.session_state.metrics_history)

# Real-time Metrics Section
st.header("Real-time System Metrics")

# Create three columns for current metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="CPU Usage",
        value=f"{current_metrics['cpu_percent']}%",
        delta=f"{current_metrics['cpu_percent'] - df['cpu_percent'].mean():.1f}%"
    )

with col2:
    st.metric(
        label="Memory Usage",
        value=f"{current_metrics['memory_percent']}%",
        delta=f"{current_metrics['memory_percent'] - df['memory_percent'].mean():.1f}%"
    )

with col3:
    st.metric(
        label="Disk Usage",
        value=f"{current_metrics['disk_percent']}%",
        delta=f"{current_metrics['disk_percent'] - df['disk_percent'].mean():.1f}%"
    )

# Resource Usage Charts
st.header("Resource Usage Charts")

# CPU and Memory Usage Over Time
fig_resources = go.Figure()

fig_resources.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['cpu_percent'],
    name='CPU Usage',
    line=dict(color='blue')
))

fig_resources.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['memory_percent'],
    name='Memory Usage',
    line=dict(color='red')
))

fig_resources.update_layout(
    title='CPU and Memory Usage Over Time',
    xaxis_title='Time',
    yaxis_title='Usage %',
    height=400
)

st.plotly_chart(fig_resources, use_container_width=True)

# Network Usage Over Time
fig_network = go.Figure()

fig_network.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['network_sent'],
    name='Network Out',
    line=dict(color='green')
))

fig_network.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['network_recv'],
    name='Network In',
    line=dict(color='orange')
))

fig_network.update_layout(
    title='Network Usage Over Time (MB)',
    xaxis_title='Time',
    yaxis_title='MB',
    height=400
)

st.plotly_chart(fig_network, use_container_width=True)

# Process Table
st.header("Top Processes")

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'PID': proc.info['pid'],
                'Name': proc.info['name'],
                'CPU %': proc.info['cpu_percent'],
                'Memory %': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(processes, key=lambda x: x['CPU %'], reverse=True)[:10]

processes_df = pd.DataFrame(get_process_info())
st.dataframe(processes_df, hide_index=True)

# Auto-refresh
st.empty()
time.sleep(1)  # Update every second
st.experimental_rerun()
