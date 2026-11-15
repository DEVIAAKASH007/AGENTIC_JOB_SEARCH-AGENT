import re
from models.schemas import GitHubProfile
from matcher.normalizer import normalize_skill


def match_skill_in_text(skill, text):
    """
    Safely match a skill in text using word boundaries and token normalization.

    Prevents short skill false positives (e.g. 'C' matching 'c'),
    prevents prefix/suffix false positives (e.g. 'Java' matching 'JavaScript'),
    and prevents tooling overlap (e.g. 'Git' matching 'GitHub').
    """
    if not skill or not text:
        return False

    norm_skill = normalize_skill(skill)
    text_lower = text.lower()

    # Special word boundary rules for short / special skills
    if norm_skill == "c":
        pattern = r"(?<![A-Za-z0-9_#+])c(?![A-Za-z0-9_#+])"
        return bool(re.search(pattern, text_lower))
    elif norm_skill == "c++":
        pattern = r"(?<![A-Za-z0-9_])(c\+\+|cpp|c plus plus)(?![A-Za-z0-9_])"
        return bool(re.search(pattern, text_lower))
    elif norm_skill == "c#":
        pattern = r"(?<![A-Za-z0-9_])(c#|csharp|c sharp)(?![A-Za-z0-9_])"
        return bool(re.search(pattern, text_lower))
    elif norm_skill == "java":
        pattern = r"\bjava\b(?!script)"
        return bool(re.search(pattern, text_lower))
    elif norm_skill == "git":
        pattern = r"\bgit\b(?!hub)"
        return bool(re.search(pattern, text_lower))

    # Standard regex word boundary for other skills
    pattern = r"\b" + re.escape(norm_skill) + r"\b"
    return bool(re.search(pattern, text_lower))


def calculate_confidence(skill, github_data):
    """
    Calculate explainable confidence score using observable GitHub evidence.

    Hierarchy & Evidence Points:
        1. Actual source-code usage          -> 35 pts (1 repo) / up to 50 pts (multi-repo)
        2. GitHub language statistics        -> 30 pts max
        3. Dependency/configuration files   -> 20 pts max (dependency alone = 25 pts -> Low)
        4. README mention                    -> 5 pts max
        5. Repository topic                  -> 5 pts max
        6. Multiple repositories             -> 5 to 15 pts boost

    Score Thresholds:
        >= 70 -> 'high' (promoted to primary skills)
        >= 40 -> 'medium' (supporting evidence)
        < 40  -> 'low' (supporting evidence)
    """

    norm_skill = normalize_skill(skill)
    if not norm_skill:
        return {
            "confidence": "low",
            "score": 0,
            "evidence_breakdown": {
                "source_code": 0,
                "language": 0,
                "dependencies": 0,
                "readme": 0,
                "topics": 0,
                "repositories": 0
            }
        }

    source_code_matches = 0
    language_matches = 0
    dependency_matches = 0
    readme_matches = 0
    topic_matches = 0
    repositories_with_evidence = set()

    for repo in github_data:
        repo_name = repo.get("name", "")
        has_repo_evidence = False

        # 1. Language evidence
        languages = repo.get("languages", {})
        if isinstance(languages, dict):
            for lang in languages:
                if normalize_skill(lang) == norm_skill:
                    language_matches += 1
                    has_repo_evidence = True

        # 2. README evidence
        readme = repo.get("readme", "")
        if isinstance(readme, str) and match_skill_in_text(norm_skill, readme):
            readme_matches += 1
            has_repo_evidence = True

        # 3. Topic evidence
        topics = repo.get("topics", [])
        if isinstance(topics, list):
            for topic in topics:
                if normalize_skill(topic) == norm_skill:
                    topic_matches += 1
                    has_repo_evidence = True

        # 4. Important files (source code vs dependency manifest)
        important_files = repo.get("important_files", {})
        if isinstance(important_files, dict):
            for filepath, content in important_files.items():
                if not isinstance(content, str):
                    continue
                fname = filepath.lower()

                # Dependency manifest
                if any(fname.endswith(dep_file) for dep_file in ["requirements.txt", "package.json", "pyproject.toml", "cargo.toml", "go.mod"]):
                    if match_skill_in_text(norm_skill, content):
                        dependency_matches += 1
                        has_repo_evidence = True
                else:
                    # Actual source code file
                    if match_skill_in_text(norm_skill, content):
                        source_code_matches += 1
                        has_repo_evidence = True

        if has_repo_evidence:
            repositories_with_evidence.add(repo_name)

    # Compute numerical breakdown
    if source_code_matches >= 2:
        source_pts = 45
    elif source_code_matches == 1:
        source_pts = 35
    else:
        source_pts = 0

    lang_pts = min(30, language_matches * 30)
    dep_pts = min(20, dependency_matches * 20)
    readme_pts = min(5, readme_matches * 5)
    topic_pts = min(5, topic_matches * 5)

    repo_count = len(repositories_with_evidence)
    if repo_count >= 3:
        repo_pts = 15
    elif repo_count == 2:
        repo_pts = 10
    elif repo_count == 1:
        repo_pts = 5
    else:
        repo_pts = 0

    total_score = source_pts + lang_pts + dep_pts + readme_pts + topic_pts + repo_pts

    if total_score >= 70:
        confidence = "high"
    elif total_score >= 40:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "confidence": confidence,
        "score": total_score,
        "evidence_breakdown": {
            "source_code": source_pts,
            "language": lang_pts,
            "dependencies": dep_pts,
            "readme": readme_pts,
            "topics": topic_pts,
            "repositories": repo_pts
        }
    }


def extract_github_skills(model, github_data):
    """
    Extract technical skills from GitHub repositories.

    Gemini identifies candidate skills and evidence from repositories.
    Python then calculates explainable confidence from observable GitHub evidence.
    """

    structured_model = model.with_structured_output(GitHubProfile)

    prompt = f"""
You are analyzing a candidate's GitHub profile.

Identify technical skills that have evidence in the provided repositories.

For every skill provide:
1. skill
2. evidence
3. repositories

IMPORTANT:
- Extract only technical skills.
- Do not invent skills.
- Do not assume that a README claim proves personal implementation.
- Prefer evidence from actual repository information.
- Use standard skill names.
- Keep evidence concise.
- Do NOT determine confidence yourself.

GitHub repository data:
{github_data}
"""

    result = structured_model.invoke(prompt)

    # Calculate explainable confidence in Python
    for skill in result.skills:
        conf_data = calculate_confidence(skill.skill, github_data)
        skill.confidence = conf_data["confidence"]
        skill.score = conf_data["score"]
        skill.evidence_breakdown = conf_data["evidence_breakdown"]

    return result