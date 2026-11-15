from jsearch.search import search_jobs
from jsearch.extractor import extract_job_skills
from matcher.matcher import calculate_weighted_match
# pyrefly: ignore [missing-import]
from langchain.tools import tool


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
    # 1. Search jobs
    # ========================================================

    jobs = search_jobs.invoke({
        "skill": skill,
        "location": location
    })


    # ========================================================
    # 2. Handle errors
    # ========================================================

    if not jobs:
        return []


    if (
        isinstance(jobs[0], dict)
        and "error" in jobs[0]
    ):
        return jobs


    results = []


    # ========================================================
    # 3. Analyze every job
    # ========================================================

    for job in jobs:

        description = job.get(
            "job_description",
            ""
        )


        # ----------------------------------------------------
        # Extract required + preferred skills via Gemini
        # ----------------------------------------------------

        job_skills = extract_job_skills(
            model,
            description
        )


        required_skills = job_skills.required_skills

        preferred_skills = job_skills.preferred_skills


        # ----------------------------------------------------
        # Calculate weighted match (exact + semantic)
        # ----------------------------------------------------

        match_result = calculate_weighted_match(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills
        )


        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        results.append({

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

            "required_skills":
                required_skills,

            "preferred_skills":
                preferred_skills,

            "match_percentage":
                match_result[
                    "match_percentage"
                ],

            "matched_required_skills":
                match_result[
                    "matched_required_skills"
                ],

            "missing_required_skills":
                match_result[
                    "missing_required_skills"
                ],

            "matched_preferred_skills":
                match_result[
                    "matched_preferred_skills"
                ],

            "missing_preferred_skills":
                match_result[
                    "missing_preferred_skills"
                ],

            # Backward-compatible keys
            "matched_skills":
                match_result[
                    "matched_skills"
                ],

            "missing_skills":
                match_result[
                    "missing_skills"
                ]
        })


    # ========================================================
    # 4. Rank jobs by match percentage (highest first)
    # ========================================================

    results.sort(
        key=lambda job:
            job["match_percentage"],
        reverse=True
    )


    return results


# ============================================================
# AGENT TOOL
# ============================================================

def create_job_matching_tool(
    model,
    candidate_skills
):
    """
    Create a Career Agent tool that searches jobs
    and matches them against the candidate profile.
    """

    @tool
    def find_and_match_jobs(
        skill: str,
        location: str
    ) -> list:
        """
        Find current jobs for a skill and location
        and rank them according to the candidate's skills.
        """

        return analyze_jobs(
            model=model,
            candidate_skills=candidate_skills,
            skill=skill,
            location=location
        )

    return find_and_match_jobs