from jsearch.search import search_jobs
from jsearch.extractor import extract_job_skills

from matcher.matcher import calculate_weighted_match


def analyze_jobs(
    model,
    candidate_skills,
    skill,
    location
):
    """
    Search jobs, extract required/preferred skills,
    calculate weighted candidate-job matches,
    and rank the jobs.
    """

    # ========================================================
    # 1. SEARCH JOBS
    # ========================================================

    jobs = search_jobs.invoke({
        "skill": skill,
        "location": location
    })

    # ========================================================
    # 2. HANDLE EMPTY RESULT
    # ========================================================

    if not jobs:
        return []

    # ========================================================
    # 3. HANDLE API ERROR
    # ========================================================

    if (
        isinstance(jobs[0], dict)
        and "error" in jobs[0]
    ):

        return jobs

    # ========================================================
    # 4. STORE RESULTS
    # ========================================================

    results = []

    # ========================================================
    # 5. ANALYZE EVERY JOB
    # ========================================================

    for job in jobs:

        # ----------------------------------------------------
        # Get job description
        # ----------------------------------------------------

        description = job.get(
            "job_description",
            ""
        )

        # ----------------------------------------------------
        # Extract job skills
        # ----------------------------------------------------

        job_skills = extract_job_skills(
            model,
            description
        )

        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        required_skills = (
            job_skills.required_skills
        )

        # ----------------------------------------------------
        # Preferred skills
        # ----------------------------------------------------

        preferred_skills = (
            job_skills.preferred_skills
        )

        # ====================================================
        # MATCH CANDIDATE
        # ====================================================

        match_result = calculate_weighted_match(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )

        # ====================================================
        # STORE RESULT
        # ====================================================

        results.append({

            # ------------------------------------------------
            # Job information
            # ------------------------------------------------

            "job_title": job.get(
                "job_title"
            ),

            "company_name": job.get(
                "company_name"
            ),

            "location": job.get(
                "location"
            ),

            "job_description": description,

            "job_link": job.get(
                "job_link"
            ),

            # ------------------------------------------------
            # Extracted skills
            # ------------------------------------------------

            "required_skills":
                required_skills,

            "preferred_skills":
                preferred_skills,

            # ------------------------------------------------
            # Match information
            # ------------------------------------------------

            "match_percentage":
                match_result[
                    "match_percentage"
                ],

            "matched_required_skills":
                match_result[
                    "matched_required_skills"
                ],

            "matched_preferred_skills":
                match_result[
                    "matched_preferred_skills"
                ],

            "missing_required_skills":
                match_result[
                    "missing_required_skills"
                ],

            "missing_preferred_skills":
                match_result[
                    "missing_preferred_skills"
                ]
        })

    # ========================================================
    # 6. RANK JOBS
    # ========================================================

    results.sort(
        key=lambda job:
            job["match_percentage"],
        reverse=True
    )

    return results