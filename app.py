"""
Blog Topic & Outline Generator
A beginner-friendly Streamlit app that uses Google Gemini to turn a topic
into a blog title, a 5-8 section outline, a target audience and a writing goal.
"""

import json
import os
from typing import List

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

# Read GEMINI_API_KEY (and optional GEMINI_MODEL) from the local .env file.
load_dotenv()

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
DEFAULT_MODEL = "gemini-3-flash-preview"  # verify with check_models.py
NOT_SPECIFIED = "Not specified by the user"
WRITING_GOALS = [
    "Inform and Educate",
    "Explain a Topic",
    "Persuade Readers",
    "Provide Practical Guidance",
    "Compare Ideas",
]
MIN_SECTIONS = 5
MAX_SECTIONS = 8


# ----------------------------------------------------------------------
# The schema: exactly four fields. Gemini is told to follow this shape.
# ----------------------------------------------------------------------
class BlogOutline(BaseModel):
    blog_title: str
    outline_sections: List[str]
    target_audience: str
    writing_goal: str


class AppError(Exception):
    """An error whose message is safe and friendly to show to the user."""


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_api_key():
    """Find the API key. Locally it comes from .env; on Streamlit Cloud
    it comes from Secrets. The key is never written in the code."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()
    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return None


def validate_inputs(topic, audience):
    """Check what the user typed. Returns a list of problems (empty = OK)."""
    problems = []
    topic = topic.strip()
    if not topic:
        problems.append("Please enter a blog topic or niche. This field is required.")
    elif len(topic) < 3:
        problems.append("The topic is too short. Please enter at least 3 characters.")
    elif len(topic) > 200:
        problems.append("The topic is too long. Please keep it under 200 characters.")
    if len(audience.strip()) > 100:
        problems.append("The audience is too long. Please keep it under 100 characters.")
    return problems


def build_prompt(topic, audience, goal):
    """Write the instructions we send to Gemini."""
    audience_text = audience if audience else "Not provided (write for a general audience)"
    return f"""You are an expert blog editor and content strategist.
Create a blog plan for the following request.

Topic: {topic}
Target audience: {audience_text}
Writing goal: {goal}

Rules:
- blog_title: one engaging, specific title without quotation marks.
- outline_sections: between {MIN_SECTIONS} and {MAX_SECTIONS} section headings in a logical
  reading order. Each must be relevant to the topic, short (under 12 words),
  and must not repeat another section.
- target_audience: the audience the article is written for.
- writing_goal: the writing goal given above.
Return only JSON."""


def explain_api_error(error):
    """Turn a Gemini API error into a friendly message.
    We never print the raw error, so nothing sensitive can leak."""
    code = getattr(error, "code", None)
    text = str(error).lower()
    if code == 429 or "quota" in text or "resource_exhausted" in text:
        return ("Quota or rate limit reached. Wait a minute and try again. "
                "If it keeps happening, your free quota may be used up for today.")
    if code in (401, 403) or "api key" in text:
        return ("The API key was rejected. Check GEMINI_API_KEY in your .env file "
                "(or Streamlit Secrets) and make sure the key is valid.")
    if code == 404:
        return ("The Gemini model was not found for your key. Run check_models.py "
                "and set GEMINI_MODEL to a model from that list.")
    if isinstance(code, int) and code >= 500:
        return "Gemini is temporarily busy or unavailable. Please try again shortly."
    return f"The Gemini API returned an error (code {code}). Please try again."


def parse_and_validate(raw_text, audience, goal):
    """Check Gemini's reply and build the final four-field result."""
    if not raw_text:
        raise AppError("Gemini returned an empty response. Please click Generate again.")
    try:
        outline = BlogOutline(**json.loads(raw_text))
    except (json.JSONDecodeError, TypeError, ValidationError):
        raise AppError("The model's response was not in the expected JSON format. "
                       "Please click Generate again.") from None

    title = outline.blog_title.strip()
    sections = [s.strip() for s in outline.outline_sections if s.strip()]

    if not title:
        raise AppError("The model did not return a blog title. Please try again.")
    if not (MIN_SECTIONS <= len(sections) <= MAX_SECTIONS):
        raise AppError(f"The model returned {len(sections)} sections, but "
                       f"{MIN_SECTIONS}-{MAX_SECTIONS} are required. Please try again.")

    # We set these two fields ourselves so they always match the user's input.
    return {
        "blog_title": title,
        "outline_sections": sections,
        "target_audience": audience if audience else NOT_SPECIFIED,
        "writing_goal": goal,
    }


def generate_outline(topic, audience, goal):
    """Call Gemini and return the validated result dictionary."""
    api_key = get_api_key()
    if not api_key or api_key == "your_actual_api_key_here":
        raise AppError("No API key found. Add your key to the .env file "
                       "(or to Streamlit Secrets when deployed).")

    model = os.getenv("GEMINI_MODEL") or DEFAULT_MODEL

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=build_prompt(topic, audience, goal),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",  # ask for JSON
                response_schema=BlogOutline,            # ...in our schema
                temperature=0.7,
            ),
        )
    except errors.APIError as error:
        raise AppError(explain_api_error(error)) from None
    except Exception:
        raise AppError("Could not reach Gemini. Check your internet connection "
                       "and try again.") from None

    return parse_and_validate(response.text, audience, goal)


# ----------------------------------------------------------------------
# User interface
# ----------------------------------------------------------------------
def show_result(result):
    """Display the generated result and the download button."""
    st.divider()
    st.header(result["blog_title"])

    st.subheader("Outline")
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(result["outline_sections"], start=1))
    st.markdown(numbered)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Target audience**")
        st.write(result["target_audience"])
    with col2:
        st.markdown("**Writing goal**")
        st.write(result["writing_goal"])

    with st.expander("View raw JSON"):
        st.json(result)

    st.download_button(
        label="⬇️ Download JSON",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="blog_outline.json",
        mime="application/json",
    )


def main():
    st.set_page_config(page_title="Blog Topic & Outline Generator",
                       page_icon="📝", layout="centered")

    st.title("📝 Blog Topic & Outline Generator")
    st.write("Turn a broad topic into an engaging blog title and a clear outline. "
             "Enter a topic, choose a goal, and let Gemini do the planning.")

    with st.form("input_form"):
        topic = st.text_input("Blog topic or niche *",
                              placeholder="e.g. Benefits of learning Python")
        audience = st.text_input("Target audience (optional)",
                                 placeholder="e.g. College students")
        goal = st.selectbox("Writing goal", WRITING_GOALS)
        submitted = st.form_submit_button("Generate Blog Outline", type="primary")

    if submitted:
        problems = validate_inputs(topic, audience)
        if problems:
            st.session_state.pop("result", None)
            for message in problems:
                st.error(message)
        else:
            try:
                with st.spinner("Generating your outline..."):
                    st.session_state["result"] = generate_outline(
                        topic.strip(), audience.strip(), goal)
            except AppError as error:
                st.session_state.pop("result", None)
                st.error(str(error))

    # The result is kept in session_state so it stays on screen after the
    # page re-runs (for example when you click the download button).
    result = st.session_state.get("result")
    if result:
        show_result(result)


main()
