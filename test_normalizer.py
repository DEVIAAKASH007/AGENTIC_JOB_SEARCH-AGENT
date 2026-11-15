from matcher.normalizer import (
    normalize_skill,
    normalize_skills
)


print("\n===== NORMALIZER TEST =====")


tests = [

    "JavaScript",

    "Java Script",

    "JavaScript (Basic)",

    "JS",

    "Python",

    "PY",

    "React.js",

    "ReactJS",

    "K8s",

    "Kubernetes",

    "LLM",

    "Large Language Model",

    "Large Language Models",

    "Amazon EC2",

    "AWS EC2",

    "Scikit Learn",

    "sklearn"
]


for skill in tests:

    print(
        f"{skill:30} -> "
        f"{normalize_skill(skill)}"
    )


print("\n===== LIST TEST =====")


skills = [

    "Python",

    "python",

    "PY",

    "JavaScript",

    "JS",

    "React.js",

    "React",

    "K8s",

    "Kubernetes"
]


print(
    normalize_skills(skills)
)