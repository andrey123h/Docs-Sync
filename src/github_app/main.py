from fastapi import FastAPI
from github_app.controllers.pull_request_controller import PullRequestController

""" entrypoint for the GitHub App."""
app = FastAPI()
pr_controller = PullRequestController()
app.include_router(pr_controller.router)

