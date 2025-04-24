import streamlit as st

st.set_page_config(
    page_title="DevOps Agent Home",
    page_icon="🏠",
    layout="wide"
)

st.title("Welcome to DevOps Agent")

st.markdown("""
## Available Pages

1. **📊 Dashboard**
   - Quick actions for project initialization and testing
   - System metrics visualization
   - Recent activity tracking

2. **🤖 DevOps Assistant**
   - Chat with AI-powered assistant
   - File analysis and validation
   - YAML code editor and validator

3. **📈 Monitoring**
   - Real-time system metrics
   - Resource usage charts
   - Process monitoring

## Getting Started

1. Use the sidebar to navigate between pages
2. Start with the Dashboard for quick actions
3. Use the DevOps Assistant for help and file analysis
4. Monitor your system performance in the Monitoring page

## Need Help?

Click on the DevOps Assistant page to chat with our AI-powered assistant for any questions or guidance.
""")

# Display current system status
st.header("System Status")
import psutil

col1, col2, col3 = st.columns(3)

with col1:
    cpu_percent = psutil.cpu_percent()
    st.metric("CPU Usage", f"{cpu_percent}%")

with col2:
    memory = psutil.virtual_memory()
    st.metric("Memory Usage", f"{memory.percent}%")

with col3:
    disk = psutil.disk_usage('/')
    st.metric("Disk Usage", f"{disk.percent}%")
