# DevOps Agent

An autonomous DevOps agent integrated with Azure OpenAI for automated software development and operations tasks.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/aarsabhi/DevOps-Agent)

## Features

- Secure containerized environment
- File and code operations
- Build and execution automation
- Testing and validation
- Version control integration
- Azure OpenAI integration

## Setup

1. Clone the repository
2. Create a `.streamlit/secrets.toml` file with your Azure OpenAI credentials:
   ```toml
   AZURE_OPENAI_KEY = "your_key_here"
   AZURE_OPENAI_ENDPOINT = "your_endpoint_here"
   AZURE_OPENAI_API_VERSION = "2024-08-01-preview"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run Home.py
   ```

## Deployment to Streamlit.io

1. Push your code to a GitHub repository
2. Go to [Streamlit.io](https://streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and specify:
   - Main file path: `Home.py`
   - Branch: `main` (or your preferred branch)
6. Add the following secrets in Streamlit.io's secrets management:
   - `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
   - `AZURE_OPENAI_API_VERSION`: "2024-08-01-preview"

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

- All operations run in an isolated environment
- Secure handling of Azure OpenAI credentials through Streamlit secrets
- Limited file system access
- Environment variables and secrets are properly managed
