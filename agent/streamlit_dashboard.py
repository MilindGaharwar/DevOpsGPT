import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import yaml
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server

# Initialize Prometheus metrics
REGISTRY = CollectorRegistry()
command_counter = Counter('devops_agent_commands_total', 'Total commands executed', registry=REGISTRY)
file_operations = Counter('devops_agent_file_operations', 'File operations', ['operation'], registry=REGISTRY)
execution_time = Histogram('devops_agent_execution_time', 'Command execution time', registry=REGISTRY)
memory_usage = Gauge('devops_agent_memory_usage_bytes', 'Memory usage in bytes', registry=REGISTRY)

class MetricsManager:
    def __init__(self):
        self.commands_history = []
        self.file_ops_history = []
        self.performance_history = []

    def record_command(self, command: str, execution_time: float):
        command_counter.inc()
        execution_time.observe(execution_time)
        self.commands_history.append({
            'timestamp': datetime.now(),
            'command': command,
            'execution_time': execution_time
        })

    def record_file_operation(self, operation: str):
        file_operations.labels(operation=operation).inc()
        self.file_ops_history.append({
            'timestamp': datetime.now(),
            'operation': operation
        })

    def record_performance(self, cpu_usage: float, memory_usage: float):
        memory_usage.set(memory_usage)
        self.performance_history.append({
            'timestamp': datetime.now(),
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage
        })

    def get_metrics_data(self):
        return {
            'commands': pd.DataFrame(self.commands_history),
            'file_ops': pd.DataFrame(self.file_ops_history),
            'performance': pd.DataFrame(self.performance_history)
        }

def main():
    st.set_page_config(
        page_title="DevOps Agent Dashboard",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize metrics manager
    if 'metrics_manager' not in st.session_state:
        st.session_state.metrics_manager = MetricsManager()

    # Sidebar
    st.sidebar.title("Dashboard Controls")
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last Hour", "Last 24 Hours", "Last 7 Days"]
    )

    # Main content
    st.title("DevOps Agent Monitoring Dashboard")

    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Commands",
            value=len(st.session_state.metrics_manager.commands_history),
            delta="↑"
        )

    with col2:
        st.metric(
            label="File Operations",
            value=len(st.session_state.metrics_manager.file_ops_history),
            delta="↑"
        )

    with col3:
        st.metric(
            label="Avg Execution Time",
            value=f"{sum([cmd['execution_time'] for cmd in st.session_state.metrics_manager.commands_history or [0]])/max(len(st.session_state.metrics_manager.commands_history), 1):.2f}s"
        )

    # Command Statistics
    st.header("Command Statistics")
    if st.session_state.metrics_manager.commands_history:
        df_commands = pd.DataFrame(st.session_state.metrics_manager.commands_history)
        fig_commands = px.line(df_commands, x='timestamp', y='execution_time', color='command',
                             title='Command Execution Times')
        st.plotly_chart(fig_commands, use_container_width=True)

    # File Operations
    st.header("File Operations")
    if st.session_state.metrics_manager.file_ops_history:
        df_files = pd.DataFrame(st.session_state.metrics_manager.file_ops_history)
        fig_files = px.histogram(df_files, x='operation', title='File Operations Distribution')
        st.plotly_chart(fig_files, use_container_width=True)

    # Performance Metrics
    st.header("Performance Metrics")
    if st.session_state.metrics_manager.performance_history:
        df_perf = pd.DataFrame(st.session_state.metrics_manager.performance_history)
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=df_perf['timestamp'], y=df_perf['cpu_usage'],
                                     name='CPU Usage', line=dict(color='blue')))
        fig_perf.add_trace(go.Scatter(x=df_perf['timestamp'], y=df_perf['memory_usage'],
                                     name='Memory Usage', line=dict(color='red')))
        fig_perf.update_layout(title='System Performance')
        st.plotly_chart(fig_perf, use_container_width=True)

    # File Upload and Analysis Section
    st.header("File Upload and Analysis")
    uploaded_file = st.file_uploader("Upload a file for analysis", type=['yaml', 'yml', 'txt', 'pdf', 'docx'])
    
    if uploaded_file is not None:
        file_contents = uploaded_file.read()
        st.write("File Analysis:")
        
        if uploaded_file.name.endswith(('.yaml', '.yml')):
            try:
                yaml_content = yaml.safe_load(file_contents)
                st.json(yaml_content)
                
                # YAML Analysis
                st.subheader("YAML Analysis")
                if isinstance(yaml_content, dict):
                    missing_fields = []
                    if not yaml_content.get('version'):
                        missing_fields.append("- Version field is missing")
                    if not yaml_content.get('description'):
                        missing_fields.append("- Description field is missing")
                    
                    if missing_fields:
                        st.warning("Suggestions for improvement:")
                        for field in missing_fields:
                            st.write(field)
                    else:
                        st.success("YAML structure looks good!")
                        
            except yaml.YAMLError as e:
                st.error(f"Error parsing YAML: {str(e)}")
        else:
            st.text(file_contents)

    # Monitoring Guide
    with st.expander("📚 Monitoring Guide"):
        st.markdown("""
        ### How to Use This Dashboard
        
        1. **Time Range Selection**
           - Use the sidebar to select different time ranges for the metrics
        
        2. **Metrics Overview**
           - Total Commands: Number of commands executed
           - File Operations: Number of file operations performed
           - Avg Execution Time: Average time taken per command
        
        3. **Command Statistics**
           - View execution times for different commands
           - Track command patterns and performance
        
        4. **File Operations**
           - Monitor file-related activities
           - Analyze operation types and frequency
        
        5. **Performance Metrics**
           - Track CPU and Memory usage
           - Identify potential bottlenecks
        
        6. **File Analysis**
           - Upload files for instant analysis
           - Get suggestions for YAML improvements
           - View file contents and structure
        """)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(9090)
    main()
