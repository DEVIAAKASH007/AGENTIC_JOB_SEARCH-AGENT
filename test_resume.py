import os
from dotenv import load_dotenv

from resume.parser import load_resume
from resume.extractor import extract_candidate_profile
from langchain.chat_models import init_chat_model


# Load variables from .env
load_dotenv()

gemini_api_key = os.getenv("gemini_api_key")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set")


# Initialize Gemini
model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=gemini_api_key
)


# Resume path
file_path = r"C:\Users\aakas\OneDrive\Desktop\career_agent\resume.pdf"


# Step 1: PDF → text
resume_text = load_resume(file_path)

print("===== RESUME TEXT =====")
print(resume_text)


# Step 2: text → CandidateProfile
profile = extract_candidate_profile(
    model,
    resume_text
)

print("\n===== CANDIDATE PROFILE =====")
print(profile)