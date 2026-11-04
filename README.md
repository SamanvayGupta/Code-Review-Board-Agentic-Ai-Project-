\# Automated Multi-Agent Code Review Board



An AI-powered automated code review system built using Python, Microsoft Agent Framework, and Google's Gemini API.



\## Features



\- \*\*Diff Reviewer:\*\* Analyzes code changes and identifies potential issues.

\- \*\*Style Reviewer:\*\* Checks code quality and coding conventions.

\- \*\*Security Reviewer:\*\* Detects security vulnerabilities.

\- \*\*Test Coverage Reviewer:\*\* Evaluates test coverage.

\- \*\*Reviewer Manager:\*\* Consolidates findings and provides a final merge recommendation.

\- \*\*GitHub Integration:\*\* Fetches Pull Requests, changed files, and source code for automated reviews.



\## Technology Stack



\- Python

\- Microsoft Agent Framework

\- Google Gemini API

\- Pydantic

\- GitHub REST API

\- Pytest

\- Streamlit



\## Running the Project



Install dependencies:



```bash

pip install -r requirements.txt

```



Configure your API credentials in a local `.env` file.



Run the agent demonstration:



```bash

python run\_agents\_demo.py

```



Run tests:



```bash

python -m pytest tests/ -v

```



\## Security Testing



The project includes an intentionally vulnerable SQL injection example to test the security review agent.



\*\*Never use the vulnerable example in production.\*\*

