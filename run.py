import subprocess
import sys
import time
from pathlib import Path

def main():
    # Start the FastAPI server
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Started FastAPI server on http://localhost:8000")
    
    # Start the Streamlit dashboard
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "agent/streamlit_dashboard.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Started Streamlit dashboard on http://localhost:8501")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.wait()
        streamlit_process.wait()
        print("Servers stopped")

if __name__ == "__main__":
    main()
