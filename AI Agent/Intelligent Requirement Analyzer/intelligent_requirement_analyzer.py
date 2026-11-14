import os
import gradio as gr

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-120b",
    temperature=0
)

# Analyze Function
def analyze_document(pdf_file):
    print("Button Clicked")
    if pdf_file is None:
        return (
            "No file uploaded",
            "",
            "",
            "",
            ""
        )

    loader = PyPDFLoader(pdf_file.name)
    docs = loader.load()

    pages = len(docs)

    return (
        f"PDF Loaded Successfully. Pages: {pages}",
        "Acceptance Criteria Test",
        "Test Case Test",
        "Risk Test",
        "Effort Test"
    )


    # Load PDF
    loader = PyPDFLoader(pdf_file.name)
    pages = loader.load()

    # Combine all text
    document_text = "\n\n".join(
        page.page_content for page in pages
    )

    # Limit text size for initial version
    document_text = document_text[:15000]

    # User Stories
    stories_prompt = f"""
    You are a Senior Business Analyst.

    Analyze the requirement document and generate detailed User Stories.

    Format:

    As a <user>
    I want <action>
    So that <benefit>

    Requirement:
    {document_text}
    """

    stories = llm.invoke(stories_prompt).content

    # Acceptance Criteria
    acceptance_prompt = f"""
    Generate Acceptance Criteria using the Given When Then format.

    Requirement:
    {document_text}
    """

    acceptance = llm.invoke(acceptance_prompt).content

    # Test Cases
    testcase_prompt = f"""
    Generate Functional Test Cases.

    Include:
    - Test Case ID
    - Scenario
    - Steps
    - Expected Result

    Requirement:
    {document_text}
    """

    testcases = llm.invoke(testcase_prompt).content

    # Risks
    risk_prompt = f"""
    Identify:

    - Functional Risks
    - Technical Risks
    - Dependency Risks
    - Security Risks

    Requirement:
    {document_text}
    """

    risks = llm.invoke(risk_prompt).content

    # Effort Estimation
    effort_prompt = f"""
    Estimate development effort.

    Include:
    - Module Name
    - Complexity
    - Story Points
    - Estimated Effort

    Requirement:
    {document_text}
    """

    effort = llm.invoke(effort_prompt).content

    return (
        stories,
        acceptance,
        testcases,
        risks,
        effort
    )

# UI
with gr.Blocks(title="AI Requirement Analyzer") as demo:

    gr.Markdown("# 🤖 AI Requirement Analyzer")
    gr.Markdown(
        "Upload BRD, FRD or Requirement Documents and generate business analysis artifacts."
    )

    pdf_input = gr.File(
        label="Upload Requirement PDF",
        file_types=[".pdf"]
    )

    analyze_btn = gr.Button(
        "Analyze Requirement",
        variant="primary"
    )

    with gr.Tab("📖 User Stories"):
        stories_output = gr.Markdown()

    with gr.Tab("✅ Acceptance Criteria"):
        acceptance_output = gr.Markdown()

    with gr.Tab("🧪 Test Cases"):
        testcases_output = gr.Markdown()

    with gr.Tab("⚠ Risks"):
        risks_output = gr.Markdown()

    with gr.Tab("📊 Estimation"):
        effort_output = gr.Markdown()

    analyze_btn.click(
        fn=analyze_document,
        inputs=pdf_input,
        outputs=[
            stories_output,
            acceptance_output,
            testcases_output,
            risks_output,
            effort_output,
        ]
    )

demo.launch()