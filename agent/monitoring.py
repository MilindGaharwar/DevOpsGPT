from dash import Dash, html, dcc
import plotly.express as px
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import pandas as pd
from pathlib import Path
import time
from typing import Dict, Any
from loguru import logger

class MonitoringDashboard:
    def __init__(self):
        # Prometheus metrics
        self.command_counter = Counter('devops_agent_commands_total', 'Total commands executed')
        self.file_operations = Counter('devops_agent_file_operations', 'File operations', ['operation'])
        self.execution_time = Histogram('devops_agent_execution_time', 'Command execution time')
        self.memory_usage = Gauge('devops_agent_memory_usage_bytes', 'Memory usage in bytes')

        # Initialize Dash app
        self.app = Dash(__name__)
        self.setup_dashboard()

    def setup_dashboard(self):
        """Setup the Dash dashboard layout"""
        self.app.layout = html.Div([
            html.H1("DevOps Agent Monitoring Dashboard"),
            
            # Command Statistics Section
            html.Div([
                html.H2("Command Statistics"),
                dcc.Graph(id='command-stats'),
                dcc.Interval(id='command-stats-update', interval=5000)
            ]),
            
            # File Operations Section
            html.Div([
                html.H2("File Operations"),
                dcc.Graph(id='file-ops'),
                dcc.Interval(id='file-ops-update', interval=5000)
            ]),
            
            # Performance Metrics Section
            html.Div([
                html.H2("Performance Metrics"),
                dcc.Graph(id='performance'),
                dcc.Interval(id='performance-update', interval=2000)
            ]),
            
            # Real-time Logs Section
            html.Div([
                html.H2("Real-time Logs"),
                html.Pre(id='log-output'),
                dcc.Interval(id='log-update', interval=1000)
            ])
        ])

    def start(self, port: int = 8050):
        """Start the monitoring dashboard"""
        # Start Prometheus metrics server
        start_http_server(9090)
        # Start Dash server
        self.app.run_server(debug=True, port=port)

    def record_command(self, command: str, execution_time: float):
        """Record command execution metrics"""
        self.command_counter.inc()
        self.execution_time.observe(execution_time)

    def record_file_operation(self, operation: str):
        """Record file operation metrics"""
        self.file_operations.labels(operation=operation).inc()

    def update_memory_usage(self, usage: float):
        """Update memory usage gauge"""
        self.memory_usage.set(usage)

class MonitoringGuide:
    @staticmethod
    def get_setup_instructions() -> Dict[str, Any]:
        return {
            "title": "Monitoring Dashboard Setup Guide",
            "steps": [
                {
                    "step": 1,
                    "title": "Start the Monitoring Services",
                    "description": "Run the following commands to start the monitoring services:",
                    "code": """
                    # Start the monitoring dashboard
                    python -m agent.monitoring

                    # Access the dashboard
                    Open http://localhost:8050 in your browser
                    """
                },
                {
                    "step": 2,
                    "title": "Configure Prometheus",
                    "description": "Access Prometheus metrics at:",
                    "code": "http://localhost:9090/metrics"
                },
                {
                    "step": 3,
                    "title": "Dashboard Sections",
                    "description": """
                    The dashboard contains four main sections:
                    1. Command Statistics: View command execution patterns
                    2. File Operations: Monitor file-related activities
                    3. Performance Metrics: Track system performance
                    4. Real-time Logs: View live agent logs
                    """
                },
                {
                    "step": 4,
                    "title": "Using the Dashboard",
                    "description": """
                    - Use the refresh intervals to control update frequency
                    - Click on graphs to zoom and explore data
                    - Export data using the built-in tools
                    - Set up alerts in Prometheus for critical metrics
                    """
                }
            ],
            "best_practices": [
                "Regular monitoring of command execution patterns",
                "Setting up alerts for unusual patterns",
                "Periodic review of performance metrics",
                "Regular backup of monitoring data"
            ]
        }
