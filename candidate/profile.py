from models.schemas import CandidateProfile, GitHubProfile


def create_unified_profile(
    resume_profile: CandidateProfile,
    github_profile: GitHubProfile
):
    """
    Build a unified candidate profile from resume and GitHub data.

    Note: the live pipeline uses profile/profile.py:build_candidate_profile
    which applies confidence-based filtering.

    This function is kept for reference / alternative usage.
    """

    resume_skills = set(
        skill.lower()
        for skill in resume_profile.skills
    )

    github_skills = {
        skill.skill.lower(): skill
        for skill in github_profile.skills
    }

    all_skills = resume_skills | set(github_skills.keys())

    unified_skills = []

    for skill in sorted(all_skills):

        sources = []
        evidence = []

        # Resume evidence
        if skill in resume_skills:

            sources.append("resume")

            evidence.append(
                "Skill listed in resume"
            )

        # GitHub evidence
        if skill in github_skills:

            github_skill = github_skills[skill]

            sources.append("github")

            evidence.append(
                github_skill.evidence
            )

        unified_skills.append({
            "skill": skill,
            "sources": sources,
            "evidence": evidence
        })

    return {
        "skills": unified_skills
    }