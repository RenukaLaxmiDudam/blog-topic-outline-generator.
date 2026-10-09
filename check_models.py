"""Lists the Gemini models your API key can use for text generation."""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads GEMINI_API_KEY from the .env file

api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_actual_api_key_here":
    raise SystemExit("Put your real key in the .env file first.")

client = genai.Client(api_key=api_key)

print("Models that support generateContent:\n")
for model in client.models.list():
    actions = getattr(model, "supported_actions", None) or []
    if "generateContent" in actions:
        print(model.name.replace("models/", ""))
