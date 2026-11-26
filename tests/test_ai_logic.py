import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "email-ai-agent")))

from ai_logic import generate_reply


class ReplyLogicTests(unittest.TestCase):
    def test_rules_meeting(self):
        self.assertIn("meeting", generate_reply("Can we have a meeting?", provider="rules").lower())

    def test_rules_thanks(self):
        self.assertEqual(generate_reply("Thanks!", provider="rules"), "You're very welcome!")

    def test_auto_fallback_when_gemini_unavailable(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key", "REPLY_PROVIDER": "auto"}):
            with patch("ai_logic._gemini_reply", side_effect=RuntimeError("temporary API failure")):
                draft, provider, warning = generate_reply("Hello", return_provider=True)
        self.assertEqual(provider, "rules-fallback")
        self.assertTrue(draft)
        self.assertIn("temporary API failure", warning)


if __name__ == "__main__":
    unittest.main()
