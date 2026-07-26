import unittest

from agents import GeneratorAgent, ReviewerAgent, run_pipeline


class AgentPipelineTests(unittest.TestCase):
    def test_generator_returns_required_shape(self):
        content = GeneratorAgent().generate({"grade": 4, "topic": "Types of angles"})
        self.assertIn("explanation", content)
        self.assertEqual(len(content["mcqs"]), 3)
        self.assertEqual(content["mcqs"][0]["answer"], "B")

    def test_valid_lesson_passes_review(self):
        content = GeneratorAgent().generate({"grade": 4, "topic": "Types of angles"})
        review = ReviewerAgent(4, "Types of angles").review(content)
        self.assertEqual(review["status"], "pass")
        self.assertEqual(review["feedback"], [])

    def test_failure_gets_one_refined_output(self):
        result = run_pipeline(
            {"grade": 4, "topic": "Types of angles"}, inject_demo_issue=True
        )
        self.assertEqual(result["reviewer_output"]["status"], "fail")
        self.assertIsNotNone(result["refined_output"])
        self.assertEqual(result["refined_review"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
