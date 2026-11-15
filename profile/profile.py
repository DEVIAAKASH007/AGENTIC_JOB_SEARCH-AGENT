from models.schemas import CandidateProfile, GitHubProfile


def build_candidate_profile(
    resume_profile: CandidateProfile,
    github_profile: GitHubProfile
):
    """
    Build a unified candidate profile.

    Resume skills are always treated as primary skills.

    GitHub skills are added to primary skills only when
    confidence is HIGH.

    MEDIUM and LOW confidence GitHub skills are kept
    separately as supporting evidence.
    """

    # ========================================================
    # PRIMARY SKILLS
    # ========================================================

    skills = set()

    # --------------------------------------------------------
    # Resume skills
    # --------------------------------------------------------

    for skill in resume_profile.skills:

        if skill and skill.strip():

            skills.add(
                skill.strip()
            )


    # ========================================================
    # GITHUB EVIDENCE
    # ========================================================

    github_evidence = []


    for github_skill in github_profile.skills:

        skill_name = github_skill.skill.strip()

        confidence = (
            github_skill.confidence
            .strip()
            .lower()
        )


        if not skill_name:
            continue


        # ----------------------------------------------------
        # HIGH confidence
        # ----------------------------------------------------

        if confidence == "high":

            skills.add(
                skill_name
            )


        # ----------------------------------------------------
        # MEDIUM / LOW confidence
        # ----------------------------------------------------

        else:

            github_evidence.append({

                "skill": skill_name,

                "confidence": confidence,

                "evidence":
                    github_skill.evidence,

                "repositories":
                    github_skill.repositories
            })


    # ========================================================
    # UNIFIED PROFILE
    # ========================================================

    return {

        "skills": sorted(skills),

        "github_evidence":
            github_evidence,

        "resume_projects":
            resume_profile.projects,

        "education":
            resume_profile.education,

        "experience":
            resume_profile.experience,

        "certifications":
            resume_profile.certifications
    }