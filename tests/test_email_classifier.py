import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "email-ai-agent")))
from email_classifier import classify_email


class EmailClassifierTests(unittest.TestCase):
    def test_job_email_high_priority(self):
        result = classify_email("recruiter@example.com", "Interview invitation", "We would like to schedule an interview.")
        self.assertEqual(result["category"], "Job")
        self.assertEqual(result["priority"], "High")

    def test_promotion_is_likely_automated(self):
        result = classify_email("newsletter@example.com", "Special discount sale", "Limited offer")
        self.assertTrue(result["automated"])
        self.assertEqual(result["category"], "Promotion")

    def test_security_suggests_verification(self):
        result = classify_email("security@example.com", "Password verification", "Verify your account password")
        self.assertEqual(result["category"], "Security")
        self.assertIn("official", result["suggested_action"].lower())

    def test_general_email_gets_generic_action(self):
        result = classify_email("someone@example.com", "Hello", "A message with no obvious category")
        self.assertEqual(result["category"], "General")
        self.assertEqual(result["priority"], "Normal")


if __name__ == "__main__":
    unittest.main()
