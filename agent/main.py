from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import os
from typing import Optional, Dict, Any
import docker
import git
from pathlib import Path
import time

from .file_handler import FileHandler
from .streamlit_dashboard import MetricsManager

app = FastAPI(title="DevOps Agent")

class Command(BaseModel):
    action: str
    filepath: Optional[str] = None
    content: Optional[str] = None
    line_range: Optional[str] = None
    file_type: Optional[str] = None

class Agent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.workspace = Path("/workspace")
        self.file_handler = FileHandler(self.workspace)
        self.metrics_manager = MetricsManager()
        
    async def execute_command(self, command: Command):
        start_time = time.time()
        try:
            result = None
            if command.action == "write":
                result = await self._write_file(command.filepath, command.content, command.line_range, command.file_type)
            elif command.action == "read":
                result = await self._read_file(command.filepath)
            elif command.action == "analyze":
                result = await self._analyze_file(command.filepath, command.content)
            elif command.action == "retrieve":
                result = await self._retrieve_content(command.content)
            elif command.action == "build":
                result = await self._build()
            elif command.action == "test":
                result = await self._run_tests()
            else:
                raise ValueError(f"Unknown command: {command.action}")
            
            # Record metrics
            execution_time = time.time() - start_time
            self.metrics_manager.record_command(command.action, execution_time)
            return result
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _write_file(self, filepath: str, content: str, line_range: Optional[str] = None):
        if not filepath:
            raise ValueError("Filepath is required for write operation")
        
        file_path = self.workspace / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if line_range:
            # Handle line range edits
            start, end = map(int, line_range.split('-'))
            with open(file_path, 'r') as f:
                lines = f.readlines()
            lines[start:end] = content.splitlines(True)
            with open(file_path, 'w') as f:
                f.writelines(lines)
        else:
            # Write entire file
            with open(file_path, 'w') as f:
                f.write(content)
        
        return {"status": "success", "message": f"File {filepath} written successfully"}

    async def _retrieve_content(self, query: str):
        # Implement content retrieval logic
        # This could search through files, logs, or other resources
        pass

    async def _build(self):
        try:
            # Example: Build using docker
            self.docker_client.images.build(
                path=".",
                tag="devops-agent:latest",
                rm=True
            )
            return {"status": "success", "message": "Build completed successfully"}
        except Exception as e:
            raise Exception(f"Build failed: {str(e)}")

    async def _run_tests(self):
        try:
            # Run tests in container
            container = self.docker_client.containers.run(
                "devops-agent:latest",
                command=["pytest"],
                volumes={str(self.workspace): {'bind': '/app/tests', 'mode': 'ro'}},
                remove=True
            )
            return {"status": "success", "message": "Tests completed successfully"}
        except Exception as e:
            raise Exception(f"Tests failed: {str(e)}")

agent = Agent()

@app.post("/execute")
async def execute_command(command: Command):
    return await agent.execute_command(command)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_path = agent.workspace / file.filename
        with open(file_path, 'wb') as f:
            f.write(contents)
        return {"status": "success", "message": f"File {file.filename} uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/guide")
async def get_monitoring_guide():
    return JSONResponse(content=MonitoringGuide.get_setup_instructions())

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
