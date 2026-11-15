import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from jobs.analyzer import analyze_jobs


load_dotenv()


# ============================================================
# MODEL
# ============================================================

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# CANDIDATE SKILLS
# ============================================================

candidate_skills = [
    "C",
    "C++",
    "CNN",
    "CSS",
    "Deep Learning",
    "HTML",
    "JavaScript",
    "Neural Networks",
    "Python",
    "RNN",
    "SQL",
    "Scikit-learn",
    "TensorFlow",
    "Tkinter"
]


# ============================================================
# ANALYZE JOBS
# ============================================================

results = analyze_jobs(
    model=model,
    candidate_skills=candidate_skills,
    skill="software engineer",
    location="Bangalore"
)


# ============================================================
# DISPLAY
# ============================================================

print("\n========================================")
print("       RANKED JOB RESULTS")
print("========================================")


for index, job in enumerate(
    results,
    start=1
):

    print("\n")
    print("=" * 60)

    print(
        f"RANK #{index}"
    )

    print("=" * 60)

    print(
        "Job:",
        job["job_title"]
    )

    print(
        "Company:",
        job["company_name"]
    )

    print(
        "Location:",
        job["location"]
    )

    print(
        "Match:",
        job["match_percentage"],
        "%"
    )

    print(
        "\nMatched Skills:"
    )

    for skill in job["matched_skills"]:

        print(
            "-",
            skill
        )

    print(
        "\nMissing Skills:"
    )

    for skill in job["missing_skills"]:

        print(
            "-",
            skill
        )