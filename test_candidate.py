from candidate.loader import load_candidate_profile


# ============================================================
# LOAD COMPLETE CANDIDATE PROFILE
# ============================================================

profile = load_candidate_profile(
    resume_path="resume.pdf",
    github_url="https://github.com/DEVIAAKASH007"
)


# ============================================================
# DISPLAY
# ============================================================

print("\n========================================")
print("      CANDIDATE PROFILE")
print("========================================")


print("\nPrimary Skills:")

for skill in profile["skills"]:

    print(
        "-",
        skill
    )


print("\nProjects:")

for project in profile["resume_projects"]:

    print(
        "-",
        project.name
    )


print("\nEducation:")

for education in profile["education"]:

    print(
        "-",
        education
    )


print("\nGitHub Supporting Evidence:")

for evidence in profile["github_evidence"]:

    print(
        "\nSkill:",
        evidence["skill"]
    )

    print(
        "Confidence:",
        evidence["confidence"]
    )

    print(
        "Evidence:",
        evidence["evidence"]
    )