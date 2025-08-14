from fastapi import FastAPI
from pull_request_handler import PullRequestHandler
from config import Config


Config.validate() # Ensure configuration is valid
app = FastAPI()
pr_handler = PullRequestHandler()
app.include_router(pr_handler.router)  # exposes /pr/webhook

# uvicorn main:app --reload --host 0.0.0.0 --port 8080