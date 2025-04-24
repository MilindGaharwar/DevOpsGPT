# DevOps Agent

An autonomous DevOps agent integrated with Azure OpenAI for automated software development and operations tasks.

## Features

- Secure containerized environment
- File and code operations
- Build and execution automation
- Testing and validation
- Version control integration
- Azure OpenAI integration

## Setup

1. Clone the repository
2. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   ```
3. Build the Docker container:
   ```bash
   docker build -t devops-agent .
   ```
4. Run the agent and dashboard:
   ```bash
   python run.py
   ```
   This will start:
   - FastAPI server on http://localhost:8000
   - Streamlit dashboard on http://localhost:8501
   - Prometheus metrics on http://localhost:9090

## Usage

The agent exposes a REST API for command execution:

```bash
# Example: Write a file
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "write", "filepath": "test.py", "content": "print(\"Hello World!\")"}'

# Example: Run tests
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "test"}'
```

## Security

- All operations run in an isolated Docker container
- Secure handling of Azure OpenAI credentials
- Limited file system access through volume mounting
