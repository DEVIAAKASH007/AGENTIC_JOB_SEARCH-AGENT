from github.extractor import match_skill_in_text, calculate_confidence


def test_github_confidence():
    print("\n========================================")
    print("      GITHUB CONFIDENCE TESTS")
    print("========================================")

    # 1. Word Boundary Tests
    print("\n1. Word Boundary Tests:")
    assert match_skill_in_text("C", "cprofile code") == False, "C matched cprofile!"
    assert match_skill_in_text("C", "main.c file in C programming") == True, "C failed to match!"
    print("  [OK] Short skill 'C' word boundary test passed.")

    # 2. 'Java' vs 'JavaScript'
    assert match_skill_in_text("Java", "JavaScript frontend app") == False, "Java matched JavaScript!"
    assert match_skill_in_text("Java", "Java Spring Boot backend") == True, "Java failed to match!"
    print("  [OK] 'Java' vs 'JavaScript' boundary test passed.")

    # 3. 'Git' vs 'GitHub'
    assert match_skill_in_text("Git", "GitHub actions CI/CD") == False, "Git matched GitHub!"
    assert match_skill_in_text("Git", "git commit and push") == True, "Git failed to match!"
    print("  [OK] 'Git' vs 'GitHub' boundary test passed.")

    # 4. Dependency-only evidence hierarchy test (must NOT be high)
    mock_dep_data = [{
        "name": "repo1",
        "languages": {},
        "readme": "",
        "topics": [],
        "important_files": {
            "requirements.txt": "tensorflow==2.15.0"
        }
    }]
    dep_conf = calculate_confidence("TensorFlow", mock_dep_data)
    print(f"\n2. Dependency-Only Evidence: {dep_conf}")
    assert dep_conf["confidence"] == "low", f"Dependency-only should be low, got {dep_conf['confidence']}"
    print("  [OK] Dependency-only evidence resulting in 'low' confidence passed.")

    # 5. Actual source-code + multi-repo evidence test (must be high)
    mock_source_data = [{
        "name": "repo1",
        "languages": {"Python": 10000},
        "readme": "Project using TensorFlow",
        "topics": ["tensorflow"],
        "important_files": {
            "requirements.txt": "tensorflow==2.15.0",
            "main.py": "import tensorflow as tf\nmodel = tf.keras.Sequential()"
        }
    }, {
        "name": "repo2",
        "languages": {"Python": 5000},
        "readme": "Another TensorFlow model",
        "topics": ["tensorflow"],
        "important_files": {
            "train.py": "import tensorflow as tf"
        }
    }]
    source_conf = calculate_confidence("TensorFlow", mock_source_data)
    print(f"\n3. Source Code + Multi-Repo Evidence: {source_conf}")
    assert source_conf["confidence"] == "high", f"Source code + multi-repo should be high, got {source_conf['confidence']}"
    print("  [OK] Source code + multi-repo resulting in 'high' confidence passed.")


if __name__ == "__main__":
    test_github_confidence()
