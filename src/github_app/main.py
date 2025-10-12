from fastapi import FastAPI
from github_app.controllers.pull_request_controller import PullRequestController
from github_app.configure.config import Config

Config.validate() # Ensure configuration is valid
app = FastAPI()
pr_controller = PullRequestController()
app.include_router(pr_controller.router)  # exposes /pr/webhook

# PYTHONPATH=src uvicorn src.github_app.main:app --reload --host 0.0.0.0 --port 8080