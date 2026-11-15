from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from matcher.normalizer import normalize_skill


# Load once
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def semantic_skill_match(
    candidate_skill,
    job_skill,
    threshold=0.80
):
    """
    Determine whether two skills are semantically similar.
    """

    candidate_skill = normalize_skill(
        candidate_skill
    )

    job_skill = normalize_skill(
        job_skill
    )

    if not candidate_skill or not job_skill:
        return False

    # Exact match
    if candidate_skill == job_skill:
        return True

    # Create embeddings
    embeddings = model.encode([
        candidate_skill,
        job_skill
    ])

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return score >= threshold