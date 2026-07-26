"""Streamlit interface for the Generator → Reviewer agent pipeline."""

import json

import streamlit as st

from agents import run_pipeline


st.set_page_config(page_title="Educational Content Agents", page_icon="📘", layout="wide")

st.title("Educational Content: Agent Pipeline")
st.caption("Generator Agent → Reviewer Agent → one feedback-led refinement pass")

with st.sidebar:
    st.header("Lesson input")
    grade = st.selectbox("Grade", options=list(range(1, 7)), index=3)
    topic = st.text_input("Topic", value="Types of angles")
    inject_demo_issue = st.checkbox(
        "Demonstrate refinement",
        help="Adds a deliberately incorrect answer key to the first draft so you can see the reviewer trigger one refinement pass.",
    )

st.markdown(
    """
    The generator receives a structured request, produces a lesson JSON object,
    and the reviewer checks it for age appropriateness, correctness, and clarity.
    """
)

if st.button("Generate and review", type="primary", use_container_width=True):
    request = {"grade": grade, "topic": topic}
    try:
        result = run_pipeline(request, inject_demo_issue=inject_demo_issue)
    except ValueError as error:
        st.error(str(error))
    else:
        st.subheader("1. Generator output")
        st.json(result["generator_output"])

        st.subheader("2. Reviewer feedback")
        review = result["reviewer_output"]
        if review["status"] == "pass":
            st.success("PASS — the draft meets the reviewer checks.")
        else:
            st.error("FAIL — the generator will receive this feedback once.")
        st.json(review)

        if result["refined_output"] is not None:
            st.subheader("3. Refined output (one permitted pass)")
            st.json(result["refined_output"])
            refined_review = result["refined_review"]
            if refined_review["status"] == "pass":
                st.success("Refined draft passed review.")
            else:
                st.warning("The single refinement pass is complete; further automatic retries are intentionally disabled.")
            with st.expander("Review of refined output"):
                st.json(refined_review)

        with st.expander("Structured request sent to the Generator Agent"):
            st.code(json.dumps(request, indent=2), language="json")

else:
    st.info("Choose a grade and click **Generate and review**. Use the demo checkbox to show the refinement path.")
