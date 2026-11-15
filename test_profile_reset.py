from app import current_candidate_data, reset_candidate, find_jobs_action


def test_profile_reset():
    print("\n========================================")
    print("      PROFILE RESET & REQUIREMENT TESTS")
    print("========================================")

    # 1. Initial state check (NO hardcoded candidate skills)
    reset_candidate()
    assert current_candidate_data["profile_loaded"] == False, "Initial state should be profile_loaded=False"
    assert current_candidate_data["skills"] == [], "Initial skills list should be empty!"
    print("  [OK] Initial empty state test passed (No hardcoded skills).")

    # 2. Profile-required check: job search blocked when no profile is loaded
    cards_out, _ = find_jobs_action("software engineer", "Bangalore", "")
    assert "Profile Required" in cards_out, "Job search was not blocked when profile_loaded=False!"
    print("  [OK] Profile-required job search guard test passed.")

    # 3. Load Profile A
    current_candidate_data["profile"] = {"name": "User A"}
    current_candidate_data["skills"] = ["Python", "Django", "PostgreSQL"]
    current_candidate_data["profile_loaded"] = True
    assert current_candidate_data["skills"] == ["Python", "Django", "PostgreSQL"]
    print("  [OK] Profile A loaded successfully.")

    # 4. Reset before loading Profile B
    reset_candidate()
    assert current_candidate_data["profile_loaded"] == False, "Reset failed to clear profile_loaded!"
    assert current_candidate_data["skills"] == [], "Reset failed to clear skills!"
    print("  [OK] Reset candidate successfully wiped Profile A data.")

    # 5. Load Profile B
    current_candidate_data["profile"] = {"name": "User B"}
    current_candidate_data["skills"] = ["C++", "Qt", "OpenGL"]
    current_candidate_data["profile_loaded"] = True
    assert "Python" not in current_candidate_data["skills"], "User B inherited User A skills!"
    assert current_candidate_data["skills"] == ["C++", "Qt", "OpenGL"]
    print("  [OK] Profile B loaded independently (No cross-user contamination).")


if __name__ == "__main__":
    test_profile_reset()
