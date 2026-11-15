import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

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


load_dotenv()


# ============================================================
# GEMINI
# ============================================================

gemini_api_key = os.getenv("GEMINI_API_KEY")

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=gemini_api_key
)


# ============================================================
# GITHUB URL
# ============================================================

github_url = "https://github.com/DEVIAAKASH007"

username = extract_username(github_url)

print("GitHub user:", username)


# ============================================================
# GET REPOSITORIES
# ============================================================

repos = get_github_repositories(username)


if isinstance(repos, dict) and "error" in repos:

    print("\nGitHub Error:")
    print(repos)

    exit()


print("Repositories found:", len(repos))


# ============================================================
# GITHUB PROFILE DATA
# ============================================================

github_profile = []


# ============================================================
# PROCESS EACH REPOSITORY
# ============================================================

for repo in repos:

    repo_name = repo["name"]

    print("\nProcessing:", repo_name)


    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    readme = get_readme(
        username,
        repo_name
    )


    # --------------------------------------------------------
    # LANGUAGES
    # --------------------------------------------------------

    languages = get_languages(
        username,
        repo_name
    )


    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    topics = get_repository_topics(
        username,
        repo_name
    )


    # --------------------------------------------------------
    # FILE TREE
    # --------------------------------------------------------

    files = get_repository_files(
        username,
        repo_name
    )


    # --------------------------------------------------------
    # IMPORTANT FILES
    # --------------------------------------------------------

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

                important_files[file_path] = content


    # --------------------------------------------------------
    # CREATE REPOSITORY DATA
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Add repository
    # --------------------------------------------------------

    github_profile.append(
        repository_data
    )


# ============================================================
# GEMINI ANALYSIS
# ============================================================

print("\n========================================")
print("      ANALYZING GITHUB WITH GEMINI")
print("========================================")


result = extract_github_skills(
    model,
    github_profile
)


# ============================================================
# DISPLAY SKILLS
# ============================================================

print("\n===== GITHUB SKILLS =====")


for skill in result.skills:

    print("\nSkill:", skill.skill)

    print(
        "Evidence:",
        skill.evidence
    )

    print(
        "Repositories:",
        skill.repositories
    )

    print(
        "Confidence:",
        skill.confidence
    )