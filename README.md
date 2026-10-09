# Blog Topic & Outline Generator

A Generative AI web app that turns a broad topic or niche into an engaging blog
title, a logical 5-8 section outline, a target audience, and a writing goal.

**Live app:** <paste your Streamlit URL here>
**GitHub:** <paste your repository URL here>

## Problem Statement
Writers, marketers, and students often struggle to convert a broad topic into an
engaging blog title and a logical article outline. This app solves that using
Google Gemini and structured JSON output.

## Features
- Inputs: topic (required), target audience (optional), writing goal (dropdown)
- One blog title and 5-8 non-repetitive outline sections
- Output follows an exact four-field JSON schema
- Numbered, readable display plus a downloadable JSON file
- Input validation and friendly errors for missing inputs, invalid API key,
  quota limits, network problems, and malformed model responses
- If no audience is given, `target_audience` is "Not specified by the user"
- API key is never hardcoded or committed

## Output Schema
```json
{
  "blog_title": "string",
  "outline_sections": ["string"],
  "target_audience": "string",
  "writing_goal": "string"
}
```

## Technology Stack
Python, Streamlit, Google Gemini API, `google-genai`, `python-dotenv`, JSON,
Git/GitHub, Streamlit Community Cloud.

## Project Structure
```
blog-topic-outline-generator/
├── app.py              # the whole application
├── check_models.py     # lists the Gemini models your key can use
├── requirements.txt
├── .env                # local secret (placeholder only in this repo)
├── .gitignore
├── README.md
└── screenshots/
```

## Installation (Windows, VS Code)
1. Install Python 3.11+ and Git.
2. Open the project folder in VS Code and open a terminal.
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```
   (If scripts are blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)
4. `pip install -r requirements.txt`
5. Get a free API key at https://aistudio.google.com/apikey
6. Edit `.env` so it contains: `GEMINI_API_KEY=your_actual_api_key_here`
   (replace with your real key, no quotes).
7. Verify models: `python check_models.py`. The app defaults to
   `gemini-3-flash-preview`. To use another model, add `GEMINI_MODEL=<name>` to `.env`.

## Usage
Run `streamlit run app.py`, open http://localhost:8501, enter a topic, optionally
an audience, choose a writing goal, and click **Generate Blog Outline**.
Click **Download JSON** to save the result.

## Testing
Run each case in the app and record the real result below.

| Test | Input | Expected | Actual result |
|---|---|---|---|
| 1 Broad topic | Artificial Intelligence / General readers | Fundamentals, applications, benefits, challenges, future trends | <fill in> |
| 2 Narrow topic | Using AI chatbots for customer support in small online stores / Small business owners | Setup, customer queries, integration, costs, limitations, measuring results | <fill in> |
| 3 Missing audience | Benefits of learning Python / (blank) | Outline generated; `target_audience` = "Not specified by the user" | <fill in> |

Also tried: empty topic, wrong API key, no internet. Screenshots are in `screenshots/`.

## Deployment (Streamlit Community Cloud)
1. Push the project to a public GitHub repository (`.env` is git-ignored).
2. At https://share.streamlit.io click **Create app**, choose the repo, branch
   `main`, main file `app.py`.
3. Open **Advanced settings → Secrets** and add: `GEMINI_API_KEY = "your_key"`
4. Deploy, then run the three tests again on the live URL.

## Security
The key is read from `.env` locally or Streamlit Secrets when deployed. It is
never in the source code, logs, or error messages.

## Limitations
Output varies between runs, free-tier quotas apply, and model names change over
time, so verify with `check_models.py`.
