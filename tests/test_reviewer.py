import unittest

from reviewer import Finding, review_code


class ReviewCodeTests(unittest.TestCase):
    def test_detects_hardcoded_secret(self):
        findings = review_code('API_KEY = "secret-value"')

        self.assertEqual(
            findings,
            [
                Finding(
                    rule_id="hardcoded-secret",
                    message="Hardcoded secret detected",
                    line=1,
                    evidence='API_KEY = "secret-value"',
                )
            ],
        )

    def test_detects_debug_print(self):
        findings = review_code('print("debug")')

        self.assertEqual(findings[0].rule_id, "debug-print")
        self.assertEqual(findings[0].line, 1)

    def test_ignores_commented_print(self):
        self.assertEqual(review_code('# print("debug")'), [])


if __name__ == "__main__":
    unittest.main()
