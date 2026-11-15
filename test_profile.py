import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pypdf import PdfReader

from resume.extractor import extract_candidate_profile
from profile.profile import build_candidate_profile

from github.analyzer import (
    extract_username,
    get_github_repositories,
    get_readme,
    get_languages,
    get_repository_topics,
    get_repository_files,
    get_repository_file
)

from github.extractor import extract_github_skills


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY
)


# ============================================================
# READ RESUME PDF
# ============================================================

resume_path = "resume.pdf"

reader = PdfReader(resume_path)

resume_text = ""

for page in reader.pages:

    text = page.extract_text()

    if text:

        resume_text += text + "\n"


print("\n========================================")
print("        EXTRACTING RESUME")
print("========================================")


# ============================================================
# GEMINI → RESUME PROFILE
# ============================================================

resume_profile = extract_candidate_profile(
    model,
    resume_text
)


print("\n===== RESUME SKILLS =====")

for skill in resume_profile.skills:

    print(
        "-",
        skill
    )


print("\n===== RESUME PROJECTS =====")

for project in resume_profile.projects:

    print(
        "-",
        project.name
    )


print("\n===== RESUME EDUCATION =====")

for education in resume_profile.education:

    print(
        "-",
        education
    )


# ============================================================
# GITHUB
# ============================================================

github_url = "https://github.com/DEVIAAKASH007"

username = extract_username(
    github_url
)


print("\n========================================")
print("        EXTRACTING GITHUB")
print("========================================")


repos = get_github_repositories(
    username
)


if (
    isinstance(repos, dict)
    and "error" in repos
):

    print("\nGitHub Error:")
    print(repos)

    exit()


github_data = []


# ============================================================
# COLLECT GITHUB DATA
# ============================================================

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


    files = get_repository_files(
        username,
        repo_name
    )


    important_files = {}


    for file_path in files:

        filename = file_path.lower()


        if filename in [
            "requirements.txt",
            "package.json",
            "pyproject.toml"
        ]:

            content = get_repository_file(
                username,
                repo_name,
                file_path
            )


            if content:

                important_files[
                    file_path
                ] = content


    repository_data = {

        "name": repo_name,

        "description": repo["description"],

        "url": repo["html_url"],

        "languages": languages,

        "topics": topics,

        "readme": readme,

        "files": files,

        "important_files": important_files
    }


    github_data.append(
        repository_data
    )


# ============================================================
# GEMINI → GITHUB PROFILE
# ============================================================

github_profile = extract_github_skills(
    model,
    github_data
)


print("\n===== GITHUB SKILLS =====")


for skill in github_profile.skills:

    print(
        "\nSkill:",
        skill.skill
    )

    print(
        "Confidence:",
        skill.confidence
    )

    print(
        "Evidence:",
        skill.evidence
    )

    print(
        "Repositories:",
        skill.repositories
    )


# ============================================================
# BUILD UNIFIED PROFILE
# ============================================================

unified_profile = build_candidate_profile(
    resume_profile,
    github_profile
)


# ============================================================
# DISPLAY UNIFIED PROFILE
# ============================================================

print("\n========================================")
print("      UNIFIED CANDIDATE PROFILE")
print("========================================")


print("\nPrimary Skills:")

for skill in unified_profile["skills"]:

    print(
        "-",
        skill
    )


print("\nGitHub Supporting Evidence:")

for evidence in unified_profile["github_evidence"]:

    print(
        "\nSkill:",
        evidence["skill"]
    )

    print(
        "Confidence:",
        evidence["confidence"]
    )

    print(
        "Evidence:",
        evidence["evidence"]
    )

    print(
        "Repositories:",
        evidence["repositories"]
    )


print("\nProjects:")

for project in unified_profile[
    "resume_projects"
]:

    print(
        "-",
        project.name
    )


print("\nEducation:")

for education in unified_profile[
    "education"
]:

    print(
        "-",
        education
    )