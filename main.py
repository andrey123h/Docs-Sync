# main.py
from fastapi import FastAPI
from  pull_request_handler import PullRequestHandler
from config import Config

app = FastAPI() #
pr_handler = PullRequestHandler() #
app.include_router(pr_handler.router)  # exposes /pr/webhook

Config.validate()
