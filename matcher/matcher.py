# matcher/matcher.py

from matcher.normalizer import normalize_skill

# ============================================================
# CONFIGURABLE PARAMETERS & INCOMPATIBLE GUARDS
# ============================================================

SEMANTIC_THRESHOLD = 0.80
REQUIRED_WEIGHT = 0.80
PREFERRED_WEIGHT = 0.20

# Explicit non-interchangeable technology pairs
INCOMPATIBLE_SKILLS = {
    ("python", "java"),
    ("java", "python"),
    ("aws", "azure"),
    ("azure", "aws"),
    ("aws", "gcp"),
    ("gcp", "aws"),
    ("aws", "google cloud"),
    ("google cloud", "aws"),
    ("azure", "gcp"),
    ("gcp", "azure"),
    ("react", "angular"),
    ("angular", "react"),
    ("git", "github"),
    ("github", "git"),
    ("sql", "nosql"),
    ("nosql", "sql")
}


def _semantic_match(candidate_skill, job_skill, threshold=SEMANTIC_THRESHOLD):
    """
    Lazy wrapper around semantic_skill_match with guard rules.

    Checks explicit non-interchangeable pairs before querying
    sentence-transformers to prevent false positives.
    """
    cand_norm = normalize_skill(candidate_skill)
    job_norm = normalize_skill(job_skill)

    if not cand_norm or not job_norm:
        return False

    if cand_norm == job_norm:
        return True

    # Guard rule check
    if (cand_norm, job_norm) in INCOMPATIBLE_SKILLS:
        return False

    from matcher.semantic_matcher import semantic_skill_match
    return semantic_skill_match(cand_norm, job_norm, threshold=threshold)


# ============================================================
# CALCULATE WEIGHTED MATCH  (primary function)
# ============================================================

def calculate_weighted_match(
    candidate_skills,
    required_skills,
    preferred_skills=None
):
    """
    Match candidate skills against job required and preferred skills.

    Pipeline:
        1. Normalize all skill lists
        2. Exact match
        3. Semantic match on remaining unmatched skills (checking guards)
        4. Weighted score: required=80%, preferred=20%
    """

    if preferred_skills is None:
        preferred_skills = []


    # ========================================================
    # 1. NORMALIZE CANDIDATE SKILLS
    # ========================================================

    candidate = set()

    for skill in candidate_skills:
        normalized = normalize_skill(skill)
        if normalized:
            candidate.add(normalized)


    # ========================================================
    # 2. NORMALIZE REQUIRED SKILLS
    # ========================================================

    required = set()

    for skill in required_skills:
        normalized = normalize_skill(skill)
        if normalized:
            required.add(normalized)


    # ========================================================
    # 3. NORMALIZE PREFERRED SKILLS
    # ========================================================

    preferred = set()

    for skill in preferred_skills:
        normalized = normalize_skill(skill)
        if normalized:
            preferred.add(normalized)


    # ========================================================
    # 4. REMOVE DUPLICATES BETWEEN REQUIRED / PREFERRED
    # ========================================================

    preferred = preferred - required


    # ========================================================
    # 5. EXACT MATCHING
    # ========================================================

    matched_required = candidate & required
    matched_preferred = candidate & preferred

    unmatched_required = required - matched_required
    unmatched_preferred = preferred - matched_preferred


    # ========================================================
    # 6. SEMANTIC MATCHING — REQUIRED
    # ========================================================

    semantic_matched_required = set()

    for job_skill in unmatched_required:
        for cand_skill in candidate:
            if job_skill in matched_required:
                break

            if _semantic_match(cand_skill, job_skill):
                semantic_matched_required.add(job_skill)
                break


    # ========================================================
    # 7. SEMANTIC MATCHING — PREFERRED
    # ========================================================

    semantic_matched_preferred = set()

    for job_skill in unmatched_preferred:
        for cand_skill in candidate:
            if job_skill in matched_preferred:
                break

            if _semantic_match(cand_skill, job_skill):
                semantic_matched_preferred.add(job_skill)
                break


    # ========================================================
    # 8. MERGE EXACT + SEMANTIC
    # ========================================================

    all_matched_required = matched_required | semantic_matched_required
    all_matched_preferred = matched_preferred | semantic_matched_preferred

    missing_required = required - all_matched_required
    missing_preferred = preferred - all_matched_preferred


    # ========================================================
    # 9. REQUIRED SCORE  (REQUIRED_WEIGHT * 100)
    # ========================================================

    if required:
        required_score = (
            len(all_matched_required)
            /
            len(required)
        ) * (REQUIRED_WEIGHT * 100)
    else:
        required_score = 0


    # ========================================================
    # 10. PREFERRED SCORE  (PREFERRED_WEIGHT * 100)
    # ========================================================

    if preferred:
        preferred_score = (
            len(all_matched_preferred)
            /
            len(preferred)
        ) * (PREFERRED_WEIGHT * 100)
    else:
        preferred_score = 0


    # ========================================================
    # 11. FINAL SCORE & SCORE BREAKDOWN EXPLANATION
    # ========================================================

    match_percentage = round(
        required_score + preferred_score,
        2
    )

    score_explanation = {
        "required_ratio": f"{len(all_matched_required)}/{len(required)}" if required else "0/0",
        "preferred_ratio": f"{len(all_matched_preferred)}/{len(preferred)}" if preferred else "0/0",
        "required_points": round(required_score, 2),
        "preferred_points": round(preferred_score, 2)
    }


    # ========================================================
    # 12. RETURN RESULT
    # ========================================================

    return {
        "match_percentage": match_percentage,
        "matched_required_skills": sorted(all_matched_required),
        "missing_required_skills": sorted(missing_required),
        "matched_preferred_skills": sorted(all_matched_preferred),
        "missing_preferred_skills": sorted(missing_preferred),
        "score_explanation": score_explanation,

        # Backward-compatible keys
        "matched_skills": sorted(all_matched_required | all_matched_preferred),
        "missing_skills": sorted(missing_required | missing_preferred)
    }


# ============================================================
# MATCH JOB  (kept for backward compatibility)
# ============================================================

def match_job(
    candidate_skills,
    required_skills,
    preferred_skills=None
):
    result = calculate_weighted_match(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )

    result["matched_required"] = result["matched_required_skills"]
    result["missing_required"] = result["missing_required_skills"]
    result["matched_preferred"] = result["matched_preferred_skills"]
    result["missing_preferred"] = result["missing_preferred_skills"]

    return result


# ============================================================
# CALCULATE MATCH  (legacy — all skills treated as required)
# ============================================================

def calculate_match(
    candidate_skills,
    required_skills
):
    candidate = set()
    for skill in candidate_skills:
        normalized = normalize_skill(skill)
        if normalized:
            candidate.add(normalized)

    required = set()
    for skill in required_skills:
        normalized = normalize_skill(skill)
        if normalized:
            required.add(normalized)

    if not required:
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": []
        }

    matched = candidate & required
    missing = required - candidate

    percentage = (len(matched) / len(required)) * 100

    return {
        "match_percentage": round(percentage, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }