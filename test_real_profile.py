import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from resume.extractor import extract_candidate_profile
from profile.profile import build_candidate_profile

from github.analyzer import (
    extract_username,
    get_github_repositories,
    get_readme,
    get_languages,
    get_repository_topics
)

from github.extractor import extract_github_skills


load_dotenv()


# =========================================
# Gemini
# =========================================

gemini_api_key = os.getenv("GEMINI_API_KEY")

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=gemini_api_key
)


# =========================================
# STEP 1: Resume
# =========================================

resume_text = """
Kondapalli Devi Aakash

B.Tech in Artificial Intelligence

Skills:
Python, C, C++, Neural Networks, RNN, CNN,
TensorFlow, HTML, CSS, JavaScript, SQL

Projects:
EEG Freezing of Gait Detection
Agentic RAG Document Intelligence Assistant
Multi-Client Chat System
Drone-based Hazard Detection System
"""


resume_profile = extract_candidate_profile(
    model,
    resume_text
)


print("\n===== RESUME PROFILE =====")

print("Skills:")

for skill in resume_profile.skills:
    print("-", skill)


# =========================================
# STEP 2: GitHub
# =========================================

github_url = "https://github.com/DEVIAAKASH007"

username = extract_username(github_url)

repos = get_github_repositories(username)


if isinstance(repos, dict) and "error" in repos:

    print("\nGitHub Error:")
    print(repos)

    exit()


github_data = []


for repo in repos:

    repo_name = repo["name"]

    readme = get_readme(
        username,
        repo_name
    )

    languages = get_languages(
        username,
        repo_name
    )

    topics = get_repository_topics(
        username,
        repo_name
    )

    repository_data = {

        "name": repo_name,

        "description": repo["description"],

        "url": repo["html_url"],

        "languages": languages,

        "topics": topics,

        "readme": readme
    }

    github_data.append(repository_data)


# =========================================
# STEP 3: GitHub AI Analysis
# =========================================

github_profile = extract_github_skills(
    model,
    github_data
)


print("\n===== GITHUB PROFILE =====")

for skill in github_profile.skills:

    print(
        "-",
        skill.skill
    )


# =========================================
# STEP 4: Build Unified Profile
# =========================================

unified_profile = build_candidate_profile(
    resume_profile,
    github_profile
)


print("\n===== UNIFIED CANDIDATE PROFILE =====")

print("\nSkills:")

for skill in unified_profile["skills"]:

    print("-", skill)


print("\nProjects:")

for project in unified_profile["resume_projects"]:

    print("-", project.name)


print("\nEducation:")

for education in unified_profile["education"]:

    print("-", education)