from matcher.semantic_matcher import semantic_skill_match


tests = [
    ("AWS EC2", "Amazon EC2"),
    ("LLM", "Large Language Model"),
    ("React.js", "React"),
    ("Python", "Java"),
    ("Python", "Python"),
]


print("\n===== SEMANTIC SKILL MATCHING =====")


for candidate, job in tests:

    result = semantic_skill_match(
        candidate,
        job
    )

    print(
        f"{candidate:25} <-> "
        f"{job:30} = {result}"
    )