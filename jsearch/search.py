import os
import requests

from dotenv import load_dotenv
from langchain.tools import tool


# Load environment variables
load_dotenv()

RAPID_API_KEY = os.getenv("RAPID_API_KEY")


@tool
def search_jobs(skill: str, location: str) -> list:
    """
    Search for current job openings based on a skill and location.
    Returns job title, company, location, description and application link.
    """

    url = "https://jsearch.p.rapidapi.com/search-v2"

    params = {
        "query": f"{skill} jobs in {location}",
        "page": "1",
        "num_pages": "1",
        "country": "in",
        "date_posted": "all"
    }

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    # -----------------------------------------
    # Check API key
    # -----------------------------------------

    if not RAPID_API_KEY:
        return [{
            "error": "missing_api_key",
            "message": "RAPID_API_KEY not found in .env"
        }]

    # -----------------------------------------
    # API request
    # -----------------------------------------

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

    except requests.RequestException as e:

        return [{
            "error": "request_failed",
            "message": str(e)
        }]

    print("Status:", response.status_code)

    # -----------------------------------------
    # HTTP error
    # -----------------------------------------

    if response.status_code != 200:

        try:
            data = response.json()
            message = data.get(
                "message",
                "JSearch API request failed"
            )

        except ValueError:
            message = response.text

        return [{
            "error": response.status_code,
            "message": message
        }]

    # -----------------------------------------
    # JSON conversion
    # -----------------------------------------

    try:

        data = response.json()

    except ValueError:

        return [{
            "error": "invalid_json",
            "message": "JSearch returned invalid JSON"
        }]

    # -----------------------------------------
    # JSearch response
    # -----------------------------------------

    print("\n===== JSEARCH RESPONSE =====")

    print("Status:", data.get("status"))

    print("Request ID:", data.get("request_id"))

    # IMPORTANT:
    # JSearch search-v2 returns jobs inside:
    #
    # data
    #   ├── jobs
    #   └── cursor

    response_data = data.get("data", {})

    if not isinstance(response_data, dict):

        return [{
            "error": "invalid_response",
            "message": "Unexpected JSearch data format"
        }]

    jobs = response_data.get("jobs", [])

    print("Raw jobs:", len(jobs))

    # -----------------------------------------
    # No jobs
    # -----------------------------------------

    if not jobs:

        print("No jobs found.")

        return []

    # -----------------------------------------
    # Normalize jobs
    # -----------------------------------------

    results = []

    for job in jobs:

        if not isinstance(job, dict):
            continue

        results.append({

            "job_title": job.get("job_title"),

            "company_name": job.get("employer_name"),

            "location": job.get("job_city"),

            "job_description": job.get("job_description"),

            "job_link": job.get("job_apply_link")

        })

    print("Jobs returned:", len(results))

    return results