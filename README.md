# *Development in progress*

*Docs-Sync* is an AI-powered service that keeps your code’s documentation in perfect alignment with the actual code behavior. It ensures Python docstrings remain perfectly in sync with actual code behavior.

## Goals
- Detects mismatches between Python code and its documentation.
- Provide accurate, ready-to-use docstring updates.
- Give clear, concise explanations for each suggested change
- Integrate seamlessly into Python developers GitHub workflows.


## Key Features
- GitHub App Integration: Connect to repositories with proper permissions, trigger scans on pull requests or commits.
- Python Change Detection: Identify only changed Python files using GitHub’s diff API.
- AST-based Parsing: Extract function, class, and method definitions with associated docstrings.
- AI-powered Analysis: Compare extracted code with existing docstrings.
- Auto-generated Docstrings:  Suggest updated documentation 
- Rationale for Changes: Explain why each update is needed.
- Approval Workflow: Developers review and approve suggested changes before merging.
