import unittest

from hindsight_memory import Memory
from recommendation_engine import generate_recommendation
from reviewer import Finding


class RecommendationTests(unittest.TestCase):
    def test_ignored_secret_history_recommends_enforcement(self):
        finding = Finding(
            rule_id="hardcoded-secret",
            message="Hardcoded secret detected",
            line=1,
            evidence='password = "admin123"',
        )
        memories = [
            Memory(
                text=(
                    "Issue: Hardcoded Password\n"
                    "Suggestion: Use environment variables.\n"
                    "Status: Ignored"
                )
            )
        ]

        recommendation = generate_recommendation(finding, memories)

        self.assertIn("Past fixes were often ignored", recommendation)
        self.assertIn("Recommend stronger enforcement", recommendation)

    def test_accepted_debug_history_reuses_solution(self):
        finding = Finding(
            rule_id="debug-print",
            message="Debug print statement detected",
            line=2,
            evidence='print("hello")',
        )
        memories = [
            Memory(
                text=(
                    "Issue: Debug Print Statement\n"
                    "Suggestion: Remove debug print statements.\n"
                    "Status: Accepted"
                )
            )
        ]

        recommendation = generate_recommendation(finding, memories)

        self.assertIn("Past fixes were mostly accepted", recommendation)


if __name__ == "__main__":
    unittest.main()
