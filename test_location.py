from matcher.matcher import calculate_weighted_match, _semantic_match


def test_location_and_guards():
    print("\n========================================")
    print("      LOCATION & SEMANTIC GUARD TESTS")
    print("========================================")

    # 1. Incompatible semantic guards
    print("\n1. Incompatible Technology Guards:")
    assert _semantic_match("Python", "Java") == False, "Python matched Java!"
    assert _semantic_match("AWS", "Azure") == False, "AWS matched Azure!"
    assert _semantic_match("React", "Angular") == False, "React matched Angular!"
    assert _semantic_match("Git", "GitHub") == False, "Git matched GitHub!"
    assert _semantic_match("SQL", "NoSQL") == False, "SQL matched NoSQL!"
    print("  [OK] Incompatible guard rules passed (Python!=Java, AWS!=Azure, React!=Angular, Git!=GitHub, SQL!=NoSQL).")

    # 2. Equivalent matching
    assert _semantic_match("AWS EC2", "Amazon EC2") == True, "AWS EC2 failed to match Amazon EC2!"
    assert _semantic_match("React.js", "React") == True, "React.js failed to match React!"
    print("  [OK] Equivalent technology semantic matching passed.")


if __name__ == "__main__":
    test_location_and_guards()
