from fastapi import FastAPI
from pull_request_controller import PullRequestController
from config import Config


Config.validate() # Ensure configuration is valid
app = FastAPI()
pr_controller = PullRequestController()
app.include_router(pr_controller.router)  # exposes /pr/webhook

# uvicorn main:app --reload --host 0.0.0.0 --port 8080