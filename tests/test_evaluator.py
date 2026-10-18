import json
import unittest

from proofloop.evaluator import parse_review_response, validate_inputs
from proofloop.prompts import build_evaluation_prompt


class InputValidationTests(unittest.TestCase):
    def test_single_mode_requires_guideline_and_answer(self):
        errors = validate_inputs(mode="single", guidelines="", answer="")
        self.assertEqual(len(errors), 2)

    def test_single_mode_accepts_real_text(self):
        errors = validate_inputs(
            mode="single", guidelines="Use only supplied evidence.", answer="A person opens a door."
        )
        self.assertEqual(errors, [])

    def test_comparison_requires_both_outputs_and_feedback(self):
        errors = validate_inputs(
            mode="comparison",
            guidelines="Compare outputs accurately.",
            output_a="A",
            output_b="",
            comparison_feedback="",
        )
        self.assertEqual(len(errors), 2)


class ResponseParsingTests(unittest.TestCase):
    def test_parse_valid_review(self):
        raw = json.dumps({
            "verdict": "Partially aligned",
            "summary": "One required detail is missing.",
            "issues": [{"title": "Missing detail", "severity": "Moderate", "guideline": "Include all key actions", "problem": "The final action is missing", "reason": "The guideline requires completeness", "suggestion": "Add the supported final action"}],
            "strengths": ["The sequence is otherwise clear."],
            "corrected_answer": "A person opens the door and walks through.",
            "confidence": "High",
            "limitations": "",
        })
        result = parse_review_response(raw)
        self.assertTrue(result["parse_ok"])
        self.assertEqual(result["verdict"], "Partially aligned")
        self.assertEqual(len(result["issues"]), 1)

    def test_bad_json_does_not_create_fake_verdict(self):
        result = parse_review_response("This is not JSON")
        self.assertFalse(result["parse_ok"])
        self.assertEqual(result["verdict"], "Review response needs inspection")
        self.assertEqual(result["corrected_answer"], "")

    def test_prompt_contains_guidelines_and_answer(self):
        prompt = build_evaluation_prompt(
            guidelines="Use only the supplied text.", mode="single", answer="The worker repairs a pipe."
        )
        self.assertIn("Use only the supplied text.", prompt)
        self.assertIn("The worker repairs a pipe.", prompt)
        self.assertIn("Return a single valid JSON object only", prompt)


if __name__ == "__main__":
    unittest.main()
