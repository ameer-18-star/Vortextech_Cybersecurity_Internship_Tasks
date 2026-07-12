"""
password_checker.py
VortexTech Cybersecurity Internship — Week 2
Author  : Ali Ameer
Track   : Beginner–Intermediate
Purpose : Evaluate password strength based on length, character variety,
          and common-password detection.

Usage:
    python password_checker.py              # runs built-in test suite
    python password_checker.py --interactive # enter passwords manually
"""

import sys

# ──────────────────────────────────────────────────────────────
# COMMON PASSWORD WORDLIST
# A small but effective list of the most commonly used passwords.
# In production, this list would be loaded from a file like
# rockyou.txt or SecLists/Passwords/Common-Credentials/
# ──────────────────────────────────────────────────────────────
COMMON_PASSWORDS = [
    "123456", "password", "123456789", "12345678", "12345",
    "1234567", "qwerty", "abc123", "111111", "123123",
    "admin", "letmein", "welcome", "monkey", "dragon",
    "master", "iloveyou", "sunshine", "princess", "football",
    "password1", "123qwe", "qwerty123", "pass", "test",
    "guest", "login", "hello", "shadow", "superman",
    "password123", "admin123", "root", "toor", "1q2w3e",
    "passw0rd", "p@ssword", "123321", "654321", "000000",
    "iloveyou1", "abc1234", "michael", "jessica", "daniel",
    "thomas", "george", "jordan", "harley", "ranger",
]


# ──────────────────────────────────────────────────────────────
# CORE EVALUATION FUNCTION
# ──────────────────────────────────────────────────────────────
def evaluate_password(password: str) -> dict:
    """
    Evaluate a password and return a results dictionary.

    Checks performed:
        0. Common password override (runs first, bypasses scoring)
        1. Minimum length — at least 8 characters
        2. Uppercase letter — at least one A-Z
        3. Lowercase letter — at least one a-z
        4. Digit          — at least one 0-9
        5. Special char   — at least one !@#$%^&* etc.

    Returns:
        dict with keys:
            score    (int)  : 0–5
            rating   (str)  : Very Weak / Weak / Medium / Strong
            feedback (list) : list of feedback strings
    """
    feedback = []
    score    = 0

    # ── Check 0: Common password override ──────────────────────
    # This runs before anything else.
    # A password like "Password1!" scores 5/5 on all checks but
    # exists in every cracking dictionary — the override catches it.
    if password.lower() in COMMON_PASSWORDS:
        return {
            "score"    : 0,
            "rating"   : "Very Weak",
            "feedback" : [
                "❌  This password is on the most-used passwords list.",
                "    Attackers try these first. Change it immediately.",
            ],
        }

    # ── Check 1: Minimum length ────────────────────────────────
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("❌  Password is too short. Use at least 8 characters.")

    # ── Check 2: Uppercase letter ──────────────────────────────
    # any() with a generator is efficient — stops at first match.
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("❌  Add at least one uppercase letter (A–Z).")

    # ── Check 3: Lowercase letter ──────────────────────────────
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("❌  Add at least one lowercase letter (a–z).")

    # ── Check 4: Digit ─────────────────────────────────────────
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("❌  Add at least one number (0–9).")

    # ── Check 5: Special character ─────────────────────────────
    special_chars = '!@#$%^&*()_+-=[]{}|;\':",./<>?~`\\'
    if any(c in special_chars for c in password):
        score += 1
    else:
        feedback.append("❌  Add at least one special character (!@#$%^&* etc.).")

    # ── Map score to rating ────────────────────────────────────
    if   score <= 2: rating = "Very Weak"
    elif score == 3: rating = "Weak"
    elif score == 4: rating = "Medium"
    else           : rating = "Strong"

    # If all checks passed, give a positive confirmation
    if not feedback:
        feedback.append("✅  All checks passed. This is a strong password.")

    return {"score": score, "rating": rating, "feedback": feedback}


# ──────────────────────────────────────────────────────────────
# DISPLAY FUNCTION
# ──────────────────────────────────────────────────────────────
def display_result(password: str, result: dict) -> None:
    """
    Print a formatted, human-readable result block.
    Password characters are masked with asterisks for safety.
    """
    bar_map = {
        "Very Weak" : "█░░░░",
        "Weak"      : "██░░░",
        "Medium"    : "███░░",
        "Strong"    : "█████",
    }

    rating      = result["rating"]
    score       = result["score"]
    bar         = bar_map.get(rating, "?????")
    masked_pwd  = "*" * len(password)

    print(f"\n  Password : {masked_pwd}  (length: {len(password)})")
    print(f"  Score    : {score}/5")
    print(f"  Rating   : [{bar}]  {rating}")
    print("  Feedback :")
    for line in result["feedback"]:
        print(f"      {line}")
    print("  " + "─" * 48)


# ──────────────────────────────────────────────────────────────
# INTERACTIVE MODE
# Lets the user type passwords manually and get instant feedback.
# Triggered by running:  python password_checker.py --interactive
# ──────────────────────────────────────────────────────────────
def interactive_mode() -> None:
    """Run an interactive loop where user enters passwords manually."""
    print("\n" + "=" * 50)
    print("  PASSWORD STRENGTH EVALUATOR — Interactive Mode")
    print("  VortexTech Internship — Week 2  |  Ali Ameer")
    print("=" * 50)
    print("  Type a password and press Enter to evaluate it.")
    print("  Type 'quit' or press Ctrl+C to exit.\n")

    while True:
        try:
            pwd = input("  Enter password: ").strip()
            if pwd.lower() in ("quit", "exit", "q"):
                print("\n  Exiting. Stay secure.\n")
                break
            if not pwd:
                print("  ⚠️   No password entered. Try again.\n")
                continue
            result = evaluate_password(pwd)
            display_result(pwd, result)
            print()
        except KeyboardInterrupt:
            print("\n\n  Exiting. Stay secure.\n")
            break


# ──────────────────────────────────────────────────────────────
# MAIN — TEST SUITE
# Runs automatically when you execute:  python password_checker.py
# Tests 8 passwords covering all possible rating outcomes.
# ──────────────────────────────────────────────────────────────
def run_test_suite() -> None:
    """Run the built-in test suite against 8 sample passwords."""
    test_passwords = [
        ("123456",          "Very Weak — common list override"),
        ("abc",             "Very Weak — too short, no variety"),
        ("hello123",        "Weak — no uppercase, no special char"),
        ("Hello123",        "Medium — missing special char only"),
        ("Hello@123",       "Strong — all 5 checks pass"),
        ("P@$$w0rd!2024",   "Strong — long, full variety"),
        ("qwerty",          "Very Weak — common list override"),
        ("SuperSecure99!",  "Strong — all 5 checks pass"),
    ]

    print("\n" + "=" * 50)
    print("  PASSWORD STRENGTH EVALUATOR")
    print("  VortexTech Internship — Week 2  |  Ali Ameer")
    print("=" * 50)
    print(f"  Running test suite — {len(test_passwords)} passwords\n")

    passed = 0
    for pwd, description in test_passwords:
        print(f"  Test: {description}")
        result = evaluate_password(pwd)
        display_result(pwd, result)
        passed += 1

    print(f"\n  ✅  Test suite complete. {passed}/{len(test_passwords)} passwords evaluated.")
    print("  Run with --interactive flag to test your own passwords.")
    print("  Example: python password_checker.py --interactive\n")


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_test_suite()
