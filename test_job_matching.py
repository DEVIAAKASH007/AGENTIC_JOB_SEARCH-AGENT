import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from jsearch.search import search_jobs
from jsearch.extractor import extract_job_skills
from matcher.matcher import calculate_weighted_match


load_dotenv()


# ============================================================
# GEMINI
# ============================================================

gemini_api_key = os.getenv(
    "GEMINI_API_KEY"
)

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=gemini_api_key
)


# ============================================================
# SEARCH PARAMETERS
# ============================================================

skill = "software engineer"
location = "Bangalore"


# ============================================================
# SEARCH JOBS
# ============================================================

jobs = search_jobs.invoke({
    "skill": skill,
    "location": location
})


# ============================================================
# HANDLE ERROR
# ============================================================

if not jobs:

    print("No jobs found.")
    exit()


if (
    isinstance(jobs[0], dict)
    and "error" in jobs[0]
):

    print("JSearch Error:")
    print(jobs[0])

    exit()


# ============================================================
# CANDIDATE SKILLS
# ============================================================

candidate_skills = [

    "C",
    "C++",
    "CNN",
    "CSS",
    "HTML",
    "JavaScript (Basic)",
    "MS Excel",
    "Neural Networks",
    "Power BI",
    "Python",
    "RNN",
    "SQL",
    "TensorFlow",
    "VS Code"
]


# ============================================================
# DISPLAY JSEARCH INFORMATION
# ============================================================

print("\n========================================")
print("       JOB MATCHING RESULTS")
print("========================================")


# ============================================================
# ANALYZE JOBS
# ============================================================

results = []


for index, job in enumerate(jobs):

    print("\n")
    print("=" * 60)
    print(f"JOB {index + 1}")
    print("=" * 60)


    # --------------------------------------------------------
    # Job information
    # --------------------------------------------------------

    title = job.get(
        "job_title",
        "Unknown"
    )

    company = job.get(
        "company_name",
        "Unknown"
    )

    job_location = job.get(
        "location",
        "Unknown"
    )

    description = job.get(
        "job_description",
        ""
    )

    job_link = job.get(
        "job_link",
        ""
    )


    print("Title:", title)
    print("Company:", company)
    print("Location:", job_location)


    # --------------------------------------------------------
    # Extract job skills
    # --------------------------------------------------------

    print("\nExtracting job skills...")


    job_skills = extract_job_skills(
        model,
        description
    )


    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_skills = (
        job_skills.required_skills
    )


    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    preferred_skills = (
        job_skills.preferred_skills
    )


    # --------------------------------------------------------
    # Display required skills
    # --------------------------------------------------------

    print("\nRequired Skills:")


    if required_skills:

        for skill_name in required_skills:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # --------------------------------------------------------
    # Display preferred skills
    # --------------------------------------------------------

    print("\nPreferred Skills:")


    if preferred_skills:

        for skill_name in preferred_skills:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # ========================================================
    # CALCULATE MATCH
    # ========================================================

    match_result = calculate_weighted_match(

        candidate_skills=
            candidate_skills,

        required_skills=
            required_skills,

        preferred_skills=
            preferred_skills
    )


    # ========================================================
    # DISPLAY MATCH
    # ========================================================

    print("\nMatch Percentage:")

    print(
        match_result[
            "match_percentage"
        ],
        "%"
    )


    # --------------------------------------------------------
    # Matched required
    # --------------------------------------------------------

    print(
        "\nMatched Required Skills:"
    )


    matched_required = (
        match_result[
            "matched_required_skills"
        ]
    )


    if matched_required:

        for skill_name in matched_required:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # --------------------------------------------------------
    # Missing required
    # --------------------------------------------------------

    print(
        "\nMissing Required Skills:"
    )


    missing_required = (
        match_result[
            "missing_required_skills"
        ]
    )


    if missing_required:

        for skill_name in missing_required:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # --------------------------------------------------------
    # Matched preferred
    # --------------------------------------------------------

    print(
        "\nMatched Preferred Skills:"
    )


    matched_preferred = (
        match_result[
            "matched_preferred_skills"
        ]
    )


    if matched_preferred:

        for skill_name in matched_preferred:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # --------------------------------------------------------
    # Missing preferred
    # --------------------------------------------------------

    print(
        "\nMissing Preferred Skills:"
    )


    missing_preferred = (
        match_result[
            "missing_preferred_skills"
        ]
    )


    if missing_preferred:

        for skill_name in missing_preferred:

            print(
                "-",
                skill_name
            )

    else:

        print("- None")


    # ========================================================
    # SAVE RESULT
    # ========================================================

    results.append({

        "job_title": title,

        "company_name": company,

        "location": job_location,

        "job_link": job_link,

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "match_percentage":
            match_result[
                "match_percentage"
            ],

        "matched_required_skills":
            matched_required,

        "missing_required_skills":
            missing_required,

        "matched_preferred_skills":
            matched_preferred,

        "missing_preferred_skills":
            missing_preferred
    })


# ============================================================
# RANK JOBS
# ============================================================

results.sort(
    key=lambda job:
        job["match_percentage"],
    reverse=True
)


# ============================================================
# FINAL RANKING
# ============================================================

print("\n\n")
print("=" * 60)
print("             FINAL JOB RANKING")
print("=" * 60)


for index, job in enumerate(results):

    print(
        f"\n{index + 1}. "
        f"{job['job_title']}"
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
        "Matched Required:",
        ", ".join(
            job[
                "matched_required_skills"
            ]
        )
        if job[
            "matched_required_skills"
        ]
        else "None"
    )

    print(
        "Missing Required:",
        ", ".join(
            job[
                "missing_required_skills"
            ]
        )
        if job[
            "missing_required_skills"
        ]
        else "None"
    )

    print(
        "Job Link:",
        job["job_link"]
    )