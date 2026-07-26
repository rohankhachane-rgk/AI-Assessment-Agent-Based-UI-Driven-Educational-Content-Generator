# Educational Content Agent Assessment

A small UI-driven Python project that demonstrates two AI-style agents working together:

1. **Generator Agent** — accepts structured lesson input and returns a deterministic lesson JSON object.
2. **Reviewer Agent** — checks the Generator result for Grade 4 appropriateness, conceptual correctness, and clarity.

If the Reviewer returns `fail`, the application sends its feedback to the Generator once. The refined draft is then reviewed, but no second automatic refinement is allowed.

## Project structure

```text
ai_assessment_agents/
├── agents.py        # Agents, input validation, and pipeline logic
├── main.py          # Streamlit UI
├── test_agents.py   # Automated behavior checks
├── requirements.txt
└── README.md
```

## Run the project

Use Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Run the tests

```bash
python -m unittest test_agents.py
```

## Structured contracts

Generator input:

```json
{
  "grade": 4,
  "topic": "Types of angles"
}
```

Generator output:

```json
{
  "explanation": "...",
  "mcqs": [
    {
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B"
    }
  ]
}
```

Reviewer output:

```json
{
  "status": "pass",
  "feedback": []
}
```

## Showing the refinement requirement

Turn on **Demonstrate refinement** in the sidebar before clicking **Generate and review**. The app inserts one known-bad answer key into only the initial draft. The Reviewer flags it, the Generator receives that feedback, and the UI displays the corrected refined draft. This makes the fail → feedback → one-pass-refinement flow visible during assessment.

The normal lesson content and the two agents remain deterministic. The demo control only exists to make the required failure branch easy to present.
