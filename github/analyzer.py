import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_headers():

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def extract_username(github_url):

    return github_url.rstrip("/").split("/")[-1]


def get_github_repositories(username):

    url = f"https://api.github.com/users/{username}/repos"

    params = {
        "per_page": 100,
        "sort": "updated"
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params
    )

    if response.status_code != 200:

        return {
            "error": response.status_code,
            "message": response.text
        }

    return response.json()


def get_readme(username, repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/readme"
    )

    headers = get_headers()

    headers["Accept"] = "application/vnd.github.raw+json"

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code != 200:
        return ""

    return response.text


def get_languages(username, repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/languages"
    )

    response = requests.get(
        url,
        headers=get_headers()
    )

    if response.status_code != 200:
        return {}

    return response.json()


def get_repository_topics(username, repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/topics"
    )

    response = requests.get(
        url,
        headers=get_headers()
    )

    if response.status_code != 200:
        return []

    data = response.json()

    return data.get("names", [])


def get_repository_files(username, repo_name):
    """
    Get files from the root of a GitHub repository.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/git/trees/main"
    )

    params = {
        "recursive": "1"
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params
    )

    # Some repositories use master instead of main
    if response.status_code == 404:

        url = (
            f"https://api.github.com/repos/"
            f"{username}/{repo_name}/git/trees/master"
        )

        response = requests.get(
            url,
            headers=get_headers(),
            params=params
        )

    if response.status_code != 200:
        return []

    data = response.json()

    tree = data.get("tree", [])

    files = []

    for item in tree:

        if item.get("type") == "blob":

            files.append(
                item.get("path", "")
            )

    return files

def get_repository_file(username, repo_name, file_path):
    """
    Get the contents of a specific file from GitHub.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/contents/{file_path}"
    )

    response = requests.get(
        url,
        headers=get_headers()
    )

    if response.status_code != 200:
        return ""

    try:
        data = response.json()
    except ValueError:
        return ""

    # GitHub returns file content as base64
    import base64

    content = data.get("content", "")

    if not content:
        return ""

    try:

        decoded = base64.b64decode(
            content
        ).decode(
            "utf-8",
            errors="ignore"
        )

        return decoded

    except Exception:

        return ""