import os

from dotenv import load_dotenv
from pypdf import PdfReader

from langchain.chat_models import init_chat_model

from resume.extractor import extract_candidate_profile
from github.extractor import extract_github_skills

from github.analyzer import (
    extract_username,
    get_github_repositories,
    get_readme,
    get_languages,
    get_repository_topics,
    get_repository_files,
    get_repository_file
)

from profile.profile import build_candidate_profile


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOAD CANDIDATE PROFILE
# ============================================================

def load_candidate_profile(
    resume_path="resume.pdf",
    github_url="https://github.com/DEVIAAKASH007"
):
    """
    Extract candidate information from:

    1. Resume PDF
    2. GitHub repositories

    Then combine them into one unified profile.
    """

    # ========================================================
    # GEMINI
    # ========================================================

    gemini_api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    model = init_chat_model(
        "google_genai:gemini-3.5-flash-lite",
        api_key=gemini_api_key
    )


    # ========================================================
    # 1. READ RESUME
    # ========================================================

    reader = PdfReader(
        resume_path
    )

    resume_text = ""


    for page in reader.pages:

        text = page.extract_text()

        if text:

            resume_text += text + "\n"


    # ========================================================
    # 2. EXTRACT RESUME PROFILE
    # ========================================================

    print(
        "\n[Candidate] Extracting resume..."
    )

    resume_profile = extract_candidate_profile(
        model,
        resume_text
    )


    # ========================================================
    # 3. GITHUB USERNAME
    # ========================================================

    username = extract_username(
        github_url
    )


    print(
        "[Candidate] Extracting GitHub..."
    )


    # ========================================================
    # 4. GET GITHUB REPOSITORIES
    # ========================================================

    repos = get_github_repositories(
        username
    )


    if (
        isinstance(repos, dict)
        and "error" in repos
    ):

        print(
            "[Candidate] GitHub error:",
            repos
        )

        return {
            "skills": resume_profile.skills,

            "github_evidence": [],

            "resume_projects":
                resume_profile.projects,

            "education":
                resume_profile.education,

            "experience":
                resume_profile.experience,

            "certifications":
                resume_profile.certifications
        }


    # ========================================================
    # 5. COLLECT GITHUB DATA
    # ========================================================

    github_data = []


    for repo in repos:

        repo_name = repo["name"]


        # ----------------------------------------------------
        # README
        # ----------------------------------------------------

        readme = get_readme(
            username,
            repo_name
        )


        # ----------------------------------------------------
        # LANGUAGES
        # ----------------------------------------------------

        languages = get_languages(
            username,
            repo_name
        )


        # ----------------------------------------------------
        # TOPICS
        # ----------------------------------------------------

        topics = get_repository_topics(
            username,
            repo_name
        )


        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        files = get_repository_files(
            username,
            repo_name
        )


        # ----------------------------------------------------
        # IMPORTANT FILES
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # REPOSITORY DATA
        # ----------------------------------------------------

        repository_data = {

            "name":
                repo_name,

            "description":
                repo["description"],

            "url":
                repo["html_url"],

            "languages":
                languages,

            "topics":
                topics,

            "readme":
                readme,

            "files":
                files,

            "important_files":
                important_files
        }


        github_data.append(
            repository_data
        )


    # ========================================================
    # 6. EXTRACT GITHUB PROFILE
    # ========================================================

    github_profile = extract_github_skills(
        model,
        github_data
    )


    # ========================================================
    # 7. BUILD UNIFIED PROFILE
    # ========================================================

    unified_profile = build_candidate_profile(
        resume_profile,
        github_profile
    )


    # ========================================================
    # 8. RETURN
    # ========================================================

    return unified_profile