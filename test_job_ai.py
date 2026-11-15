import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from jsearch.search import search_jobs
from jsearch.extractor import extract_job_skills


load_dotenv()


# -----------------------------------------
# Gemini
# -----------------------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=gemini_api_key
)


# -----------------------------------------
# Search jobs
# -----------------------------------------

jobs = search_jobs.invoke({
    "skill": "software engineer",
    "location": "Bangalore"
})


if not jobs:

    print("No jobs found.")

else:

    # -----------------------------------------
    # Test first job only
    # -----------------------------------------

    job = jobs[0]

    print("\n===== JOB =====")

    print("Title:", job.get("job_title"))

    print("Company:", job.get("company_name"))

    print("Location:", job.get("location"))


    # -----------------------------------------
    # Get job description
    # -----------------------------------------

    description = job.get("job_description")


    if not description:

        print("\nNo job description available.")

    else:

        print("\n===== EXTRACTING SKILLS =====")

        result = extract_job_skills(
            model,
            description
        )


        print("\n===== REQUIRED SKILLS =====")

        for skill in result.skills:

            print("-", skill)