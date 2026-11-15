from matcher.matcher import match_job


candidate_skills = [
    "Python",
    "JavaScript (Basic)",
    "SQL"
]


required_skills = [
    "Python",
    "JavaScript",
    "React"
]


result = match_job(
    candidate_skills,
    required_skills
)


print("\n===== MATCH RESULT =====")

print(
    "Match Percentage:",
    result["match_percentage"],
    "%"
)


print("\nMatched Skills:")

for skill in result["matched_skills"]:

    print("-", skill)


print("\nMissing Skills:")

for skill in result["missing_skills"]:

    print("-", skill)