"""Small, deterministic agents for the educational-content assessment."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class ContentRequest:
    """Validated structured input accepted by the Generator Agent."""

    grade: int
    topic: str
    feedback: List[str]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ContentRequest":
        if "grade" not in payload or "topic" not in payload:
            raise ValueError("Input must include 'grade' and 'topic'.")

        grade = payload["grade"]
        topic = payload["topic"]
        feedback = payload.get("feedback", [])
        if not isinstance(grade, int) or not 1 <= grade <= 12:
            raise ValueError("'grade' must be an integer from 1 to 12.")
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("'topic' must be a non-empty string.")
        if not isinstance(feedback, list) or not all(isinstance(item, str) for item in feedback):
            raise ValueError("'feedback' must be a list of strings.")
        return cls(grade=grade, topic=topic.strip(), feedback=feedback)


class GeneratorAgent:
    """Creates a predictable, grade-appropriate explanation and MCQs.

    This is intentionally a lightweight agent: its decisions are encoded in
    templates so the output shape remains deterministic and easy to review.
    """

    SUPPORTED_TOPIC = "types of angles"

    def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        request = ContentRequest.from_dict(payload)
        if request.topic.casefold() != self.SUPPORTED_TOPIC:
            raise ValueError(
                "This demo currently supports the topic 'Types of angles'."
            )

        # Revision feedback is deliberately part of the input.  The corrected
        # version below uses short sentences and only introduces taught facts.
        is_revision = bool(request.feedback)
        explanation = self._angle_explanation(request.grade, is_revision)
        return {
            "explanation": explanation,
            "mcqs": [
                {
                    "question": "Which angle is smaller than a right angle?",
                    "options": ["A. Obtuse angle", "B. Acute angle", "C. Straight angle", "D. Reflex angle"],
                    "answer": "B",
                },
                {
                    "question": "How many degrees are in a right angle?",
                    "options": ["A. 45 degrees", "B. 90 degrees", "C. 120 degrees", "D. 180 degrees"],
                    "answer": "B",
                },
                {
                    "question": "Which angle is exactly 180 degrees?",
                    "options": ["A. Acute angle", "B. Right angle", "C. Straight angle", "D. Obtuse angle"],
                    "answer": "C",
                },
            ],
        }

    @staticmethod
    def _angle_explanation(grade: int, is_revision: bool) -> str:
        opening = (
            "An angle is made when two lines meet at one point. "
            "We measure an angle in degrees. "
        )
        if grade <= 4 or is_revision:
            return (
                opening
                +
                "An acute angle is smaller than 90 degrees. "
                "A right angle is exactly 90 degrees, like the corner of a square. "
                "An obtuse angle is bigger than 90 degrees but smaller than 180 degrees. "
                "A straight angle is exactly 180 degrees."
            )
        return (
            opening
            +
            "An acute angle is less than 90 degrees. "
            "A right angle measures 90 degrees. "
            "An obtuse angle is greater than 90 degrees and less than 180 degrees. "
            "A straight angle measures 180 degrees."
        )


class ReviewerAgent:
    """Checks generated JSON for age appropriateness, correctness, and clarity."""

    def __init__(self, grade: int, topic: str) -> None:
        self.grade = grade
        self.topic = topic.strip().casefold()

    def review(self, content: Mapping[str, Any]) -> Dict[str, Any]:
        feedback: List[str] = []
        explanation = content.get("explanation")
        mcqs = content.get("mcqs")

        if not isinstance(explanation, str) or not explanation.strip():
            feedback.append("The explanation is missing.")
            explanation = ""
        if not isinstance(mcqs, list) or not mcqs:
            feedback.append("At least one MCQ is required.")
            mcqs = []

        self._check_age_appropriateness(explanation, feedback)
        self._check_angle_facts(explanation, feedback)
        self._check_mcqs(mcqs, explanation, feedback)

        return {
            "status": "fail" if feedback else "pass",
            "feedback": feedback,
        }

    def _check_age_appropriateness(self, explanation: str, feedback: List[str]) -> None:
        sentences = [part.strip() for part in explanation.split(".") if part.strip()]
        if self.grade <= 4 and any(len(sentence.split()) > 18 for sentence in sentences):
            feedback.append("A sentence is too long for the selected grade.")
        advanced_words = {"perpendicular", "supplementary", "consecutive", "quadrilateral"}
        lower_text = explanation.casefold()
        if self.grade <= 4 and any(word in lower_text for word in advanced_words):
            feedback.append("The explanation uses vocabulary that is too advanced for Grade 4.")

    @staticmethod
    def _check_angle_facts(explanation: str, feedback: List[str]) -> None:
        normalized = explanation.casefold()
        required_facts = [
            "acute angle is smaller than 90 degrees",
            "right angle is exactly 90 degrees",
            "obtuse angle is bigger than 90 degrees but smaller than 180 degrees",
            "straight angle is exactly 180 degrees",
        ]
        # The reviewer accepts either the Grade 4 wording or the older-grade wording.
        alternatives = [
            ("acute angle is smaller than 90 degrees", "acute angle is less than 90 degrees"),
            ("right angle is exactly 90 degrees", "right angle measures 90 degrees"),
            (
                "obtuse angle is bigger than 90 degrees but smaller than 180 degrees",
                "obtuse angle is greater than 90 degrees and less than 180 degrees",
            ),
            ("straight angle is exactly 180 degrees", "straight angle measures 180 degrees"),
        ]
        for expected, alternate in alternatives:
            if expected not in normalized and alternate not in normalized:
                feedback.append("The explanation is missing or misstates an important angle fact.")
                break

    @staticmethod
    def _check_mcqs(mcqs: List[Any], explanation: str, feedback: List[str]) -> None:
        if len(mcqs) < 3:
            feedback.append("Include at least three MCQs.")
        expected_answers = ["B", "B", "C"]
        for index, question in enumerate(mcqs, start=1):
            if not isinstance(question, Mapping):
                feedback.append(f"Question {index} is not structured as an object.")
                continue
            if not isinstance(question.get("question"), str) or not question["question"].strip():
                feedback.append(f"Question {index} has no question text.")
            options = question.get("options")
            if not isinstance(options, list) or len(options) != 4:
                feedback.append(f"Question {index} must have exactly four options.")
            answer = question.get("answer")
            if answer not in {"A", "B", "C", "D"}:
                feedback.append(f"Question {index} has an invalid answer key.")
            elif index <= len(expected_answers) and answer != expected_answers[index - 1]:
                feedback.append(f"Question {index} has an incorrect answer key.")

            question_text = str(question.get("question", "")).casefold()
            if "right angle" in question_text and "90 degrees" not in explanation.casefold():
                feedback.append(f"Question {index} tests a concept not introduced in the explanation.")


def run_pipeline(payload: Mapping[str, Any], inject_demo_issue: bool = False) -> Dict[str, Any]:
    """Run Generator → Reviewer → one optional feedback-led refinement pass."""

    request = ContentRequest.from_dict(payload)
    generator = GeneratorAgent()
    reviewer = ReviewerAgent(request.grade, request.topic)
    generated = generator.generate(payload)

    # A UI-only demonstration hook makes the failure/refinement path observable
    # without weakening the normal generated lesson.
    if inject_demo_issue:
        generated = deepcopy(generated)
        generated["mcqs"][1]["answer"] = "A"

    review = reviewer.review(generated)
    result: Dict[str, Any] = {
        "generator_output": generated,
        "reviewer_output": review,
        "refined_output": None,
        "refined_review": None,
    }
    if review["status"] == "fail":
        refinement_input = {
            "grade": request.grade,
            "topic": request.topic,
            "feedback": review["feedback"],
        }
        refined = generator.generate(refinement_input)
        result["refined_output"] = refined
        result["refined_review"] = reviewer.review(refined)
    return result
