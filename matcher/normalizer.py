# matcher/normalizer.py


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {

    # --------------------------------------------------------
    # Programming languages
    # --------------------------------------------------------

    "js": "javascript",
    "java script": "javascript",
    "javascript basic": "javascript",

    "ts": "typescript",
    "type script": "typescript",

    "py": "python",

    "c plus plus": "c++",
    "cpp": "c++",

    "c sharp": "c#",
    "csharp": "c#",

    # --------------------------------------------------------
    # AI / ML
    # --------------------------------------------------------

    "llm": "large language model",
    "llms": "large language model",
    "large language models":
        "large language model",

    "generative ai": "generative ai",
    "gen ai": "generative ai",

    "machine learning":
        "machine learning",

    "ml": "machine learning",

    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------

    "aws":
        "aws",

    "amazon web services":
        "aws",

    "amazon ec2":
        "ec2",

    "aws ec2":
        "ec2",

    # --------------------------------------------------------
    # Kubernetes
    # --------------------------------------------------------

    "k8s":
        "kubernetes",

    "kube":
        "kubernetes",

    # --------------------------------------------------------
    # React
    # --------------------------------------------------------

    "react.js":
        "react",

    "reactjs":
        "react",

    # --------------------------------------------------------
    # Node
    # --------------------------------------------------------

    "node":
        "node.js",

    "nodejs":
        "node.js",

    # --------------------------------------------------------
    # Express
    # --------------------------------------------------------

    "expressjs":
        "express",

    "express.js":
        "express",

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    "postgres":
        "postgresql",

    "mongo":
        "mongodb",

    # --------------------------------------------------------
    # Scikit-learn
    # --------------------------------------------------------

    "sklearn":
        "scikit-learn",

    "scikit learn":
        "scikit-learn",

    # --------------------------------------------------------
    # TensorFlow
    # --------------------------------------------------------

    "tensorflow":
        "tensorflow",

    # --------------------------------------------------------
    # HTML / CSS
    # --------------------------------------------------------

    "html5":
        "html",

    "css3":
        "css",

    # --------------------------------------------------------
    # CI/CD
    # --------------------------------------------------------

    "continuous integration":
        "ci/cd",

    "continuous deployment":
        "ci/cd",

    # --------------------------------------------------------
    # APIs
    # --------------------------------------------------------

    "rest api":
        "rest apis",

    "rest apis":
        "rest apis",

    "restful api":
        "rest apis",

    "restful apis":
        "rest apis"
}


# ============================================================
# NORMALIZE ONE SKILL
# ============================================================

def normalize_skill(skill):
    """
    Convert a skill into a consistent representation.
    """

    if not skill:
        return ""

    # --------------------------------------------------------
    # Convert to string
    # --------------------------------------------------------

    skill = str(skill)

    # --------------------------------------------------------
    # Lowercase
    # --------------------------------------------------------

    skill = skill.lower()

    # --------------------------------------------------------
    # Remove surrounding spaces
    # --------------------------------------------------------

    skill = skill.strip()

    # --------------------------------------------------------
    # Normalize common punctuation
    # --------------------------------------------------------

    skill = skill.replace("–", "-")
    skill = skill.replace("—", "-")

    # --------------------------------------------------------
    # Remove unnecessary spaces
    # --------------------------------------------------------

    skill = " ".join(
        skill.split()
    )

    # --------------------------------------------------------
    # Remove parentheses for cases like:
    #
    # JavaScript (Basic)
    #
    # --------------------------------------------------------

    if "(" in skill:

        skill = skill.split(
            "(",
            1
        )[0].strip()

    # --------------------------------------------------------
    # Apply alias
    # --------------------------------------------------------

    if skill in SKILL_ALIASES:

        skill = SKILL_ALIASES[
            skill
        ]

    return skill


# ============================================================
# NORMALIZE SKILL LIST
# ============================================================

def normalize_skills(skills):
    """
    Normalize a list of skills and remove duplicates.

    Example:

    [
        "Python",
        "python",
        "PY",
        "JavaScript",
        "JS"
    ]

    becomes:

    {
        "python",
        "javascript"
    }
    """

    normalized = set()

    if not skills:
        return normalized

    for skill in skills:

        normalized_skill = normalize_skill(
            skill
        )

        if normalized_skill:

            normalized.add(
                normalized_skill
            )

    return normalized