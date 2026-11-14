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

# Initial modules data for estimation fallback & interactivity
# modules_data = [
#     {"id": 1, "name": "User Management & Security", "scope": "Login, role-based access, password policy, SSO", "complexity": "Medium", "sp": 12},
#     {"id": 2, "name": "Contact & Financial Details Workflow", "scope": "UI for contact/financial data, validation, DB schema", "complexity": "Medium-High", "sp": 18},
#     {"id": 3, "name": "Loan Application Form", "scope": "Dropdowns, EMI calculation, max-loan validation", "complexity": "Medium", "sp": 14},
#     {"id": 4, "name": "Eligibility Determination Workflow", "scope": "Verification view, credit-score grid, audit trail", "complexity": "High", "sp": 20},
#     {"id": 5, "name": "Supporting Document Upload", "scope": "Multi-file upload, virus scan stub, permissions", "complexity": "Medium", "sp": 12},
#     {"id": 6, "name": "Document Verification Workflow", "scope": "Grid of docs, officer approval UI, auto-assign", "complexity": "High", "sp": 18},
#     {"id": 7, "name": "Sanctioning Agreement Form", "scope": "Consolidated view, PDF generation, data merge", "complexity": "High", "sp": 22},
#     {"id": 8, "name": "Loan Agreement Approval (Customer)", "scope": "Customer sign, e-sign placeholder, reminder SLA", "complexity": "Medium-High", "sp": 16},
#     {"id": 9, "name": "Financial Department Approval", "scope": "Finance review, status change, audit entry", "complexity": "Medium", "sp": 12},
#     {"id": 10, "name": "Core System Services", "scope": "Loan-ID generation, scheduler jobs, triggers, SLAs", "complexity": "High", "sp": 24},
#     {"id": 11, "name": "Audit-Trail & Data-Retention", "scope": "Central audit table, CRUD logging, purge job", "complexity": "Medium", "sp": 10},
#     {"id": 12, "name": "News-Feed Engine", "scope": "Feed creation, comments, WebSocket/polling", "complexity": "High", "sp": 20},
#     {"id": 13, "name": "Dashboard & Summary Views", "scope": "Loan request list, status badges, statistics tiles", "complexity": "Medium", "sp": 14},
#     {"id": 14, "name": "Additional Views", "scope": "Read-only pages, navigation, filters", "complexity": "Medium", "sp": 12},
#     {"id": 15, "name": "Reporting & Analytics", "scope": "Charts, dynamic month filter, export CSV/PDF", "complexity": "High", "sp": 26},
#     {"id": 16, "name": "Credit-Score & Existing-Loan Integration", "scope": "Backend service, caching, unit tests", "complexity": "Medium", "sp": 10},
#     {"id": 17, "name": "Mobile-Responsive UI & Cross-Browser", "scope": "CSS framework, cross-device testing, accessibility", "complexity": "Medium", "sp": 12},
#     {"id": 18, "name": "Testing & QA Automation", "scope": "Test-case design, Selenium scripts, CI pipeline", "complexity": "High", "sp": 30},
#     {"id": 19, "name": "Project Setup & DevOps", "scope": "Build pipeline, Docker, DB migrations", "complexity": "Medium", "sp": 8},
#     {"id": 20, "name": "Documentation & Knowledge Transfer", "scope": "FRD traceability, user guides, release notes", "complexity": "Low", "sp": 6},
# ]

def calculate_dynamic_estimates(team_velocity, contingency_pct):
    total_sp = sum(m["sp"] for m in modules_data)
    contingency_days = total_sp * (contingency_pct / 100.0)
    grand_total_days = total_sp + contingency_days
    
    total_sprints = grand_total_days / team_velocity if team_velocity > 0 else 1
    calendar_weeks = total_sprints * 2  # Assuming 2-week sprints
    
    summary_md = f"""
### 📊 Dynamic Project Estimate Summary
* **Total Story Points:** {total_sp} SP | **Contingency ({contingency_pct}%):** {contingency_days:.1f} days | **Grand Total:** **{grand_total_days:.1f} days** (~{calendar_weeks:.1f} weeks)
    """
    
    table_rows = [[m["id"], m["name"], m["scope"], m["complexity"], m["sp"]] for m in modules_data]
    return summary_md, table_rows

# Analyze Function with LangChain & Processing Status
def analyze_document(pdf_file):
    print("Button Clicked")

    if pdf_file is None:
        return (
            "⚠️ No file uploaded.",
            "",
            "",
            "",
            "",
            ""
        )


    # Load PDF
    loader = PyPDFLoader(pdf_file.name)
    pages = loader.load()
    document_text = "\n\n".join(page.page_content for page in pages)[:15000]

    # User Stories
    stories = llm.invoke(f"You are a Senior Business Analyst. Analyze the requirement document and generate detailed User Stories (As a <user> I want <action> So that <benefit>):\n{document_text}").content

    # Acceptance Criteria
    acceptance = llm.invoke(f"Generate Acceptance Criteria using the Given When Then format for:\n{document_text}").content

    # Test Cases
    testcases = llm.invoke(f"Generate Functional Test Cases (ID, Scenario, Steps, Expected Result):\n{document_text}").content

    # Risks
    risks = llm.invoke(f"Identify Functional, Technical, Dependency, and Security Risks for:\n{document_text}").content

    # Effort Estimation
    effort = llm.invoke(f"Estimate development effort (Module Name, Complexity, Story Points, Estimated Effort):\n{document_text}").content
    
    status_msg = f"✅ PDF Loaded Successfully ({len(pages)} pages). Analysis Complete!"
    return (
        status_msg,
        stories,
        acceptance,
        testcases,
        risks,
        effort
    )
# Custom CSS forcing high contrast and correct text colors inside tables
custom_css = """

/* ==========================
   BACKGROUND
========================== */

.gradio-container {

    background:
    linear-gradient(
        rgba(255,255,255,0.75),
        rgba(255,255,255,0.75)
    ),
    url("file=assets/office_background.jpg");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;

    min-height: 100vh;
}


/* ==========================
   GLASS PANELS
========================== */

.block {

    background: rgba(255,255,255,0.92) !important;

    backdrop-filter: blur(14px);

    border-radius: 18px;

    border: 1px solid rgba(255,255,255,0.6);

    box-shadow:
    0px 8px 24px rgba(0,0,0,0.10);

}


/* ==========================
   FORCE DARK TEXT
========================== */

* {

    color: #0f172a !important;

}


/* ==========================
   HEADINGS
========================== */

h1 {

    color: #0f172a !important;

    text-align: center;

    font-size: 35px !important;

    font-weight: 700 !important;
}

h2,h3,h4 {

    color: #1e293b !important;
}


/* ==========================
   MARKDOWN OUTPUT
========================== */

.prose,
.prose p,
.prose li,
.prose span {

    color: #111827 !important;
}

.markdown {

    background: white !important;

    color: black !important;

    border-radius: 12px;

    padding: 15px;
}


/* ==========================
   TEXTBOXES
========================== */

textarea,
textarea *,
input,
label,
span,
p,
div {

    color: #000000 !important;

}

textarea {

    background: #ffffff !important;

    color: #000000 !important;

    font-size: 15px !important;

    font-weight: 500 !important;
}


/* ==========================
   STATUS BOX
========================== */

textarea[readonly] {

    background: #f0f9ff !important;

    color: #0f172a !important;

    font-weight: 700 !important;

    border: 2px solid #38bdf8;
}


/* ==========================
   FILE UPLOAD
========================== */

.upload-box {

    background: white !important;

    border: 2px dashed #38bdf8 !important;

    color: #0f172a !important;

    border-radius: 15px;
}


/* ==========================
   TABLES
========================== */

table {

    background: white !important;

    border-radius: 10px;
}

table th {

    background: #0ea5e9 !important;

    color: white !important;

    font-weight: bold !important;
}

table td {

    background: white !important;

    color: #111827 !important;

    font-size: 14px;
}

table tr:nth-child(even) td {

    background: #f8fafc !important;
}


/* ==========================
   BUTTON
========================== */

button.primary {

    background: linear-gradient(
        135deg,
        #0ea5e9,
        #38bdf8
    ) !important;

    color: white !important;

    font-weight: bold !important;

    border-radius: 12px !important;

    transition: all 0.3s ease;
}


/* Hover */

button.primary:hover {

    background: linear-gradient(
        135deg,
        #0284c7,
        #0ea5e9
    ) !important;

    transform: translateY(-2px);
}


/* Clicked */

button.primary:active {

    background: #22c55e !important;

    color: white !important;

    transform: scale(0.95);
}


/* ==========================
   TABS
========================== */

[role="tab"] {

    background: white !important;

    color: #334155 !important;

    border-radius: 12px !important;

    margin-right: 5px;

    font-weight: 600;
}


/* ACTIVE TAB */

[role="tab"][aria-selected="true"] {

    background: #0ea5e9 !important;

    color: white !important;

    font-weight: bold !important;
}


/* ==========================
   SCROLLBAR
========================== */

::-webkit-scrollbar {

    width: 10px;
}

::-webkit-scrollbar-thumb {

    background: #0ea5e9;

    border-radius: 10px;
}

"""

# UI with Clean Professional Layout
with gr.Blocks(
    title="AI Requirement Analyzer",
    theme=gr.themes.Soft(
        primary_hue="sky",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css=custom_css
) as demo:

    gr.Markdown("# 📋 AI Requirement Analyzer & BA Workbench")
    
    with gr.Row():
        pdf_input = gr.File(label="Upload Requirement PDF (.pdf)", file_types=[".pdf"], scale=3)
        analyze_btn = gr.Button("🚀 Analyze Requirement", variant="primary", scale=1)

    status_output = gr.Textbox(value="Ready to analyze document...", label="Status", interactive=False)

    with gr.Tabs():
        with gr.Tab("📖 User Stories"):
            stories_output = gr.Textbox(
                lines=25,
                label="User Stories"
            )

        with gr.Tab("✅ Acceptance Criteria"):
            acceptance_output = gr.Textbox(
                lines=25,
                label="Acceptance Criteria"
            )
        with gr.Tab("🧪 Test Cases"):
            testcases_output = gr.Textbox(
                lines=25,
                label="Test Cases"
            )
        with gr.Tab("⚠ Risks"):
            risks_output = gr.Textbox(
                lines=25,
                label="Risk"
            )
        with gr.Tab("📊 AI Effort Estimate"):
            effort_output = gr.Textbox(
                lines=25,
                label="AI Effort Estimation"
            )
        
    # Connect analyze button with loading state indicator
    analyze_btn.click(
        fn=analyze_document,
        inputs=pdf_input,
        outputs=[
            status_output,
            stories_output,
            acceptance_output,
            testcases_output,
            risks_output,
            effort_output,
        ],
        show_progress="full"
    )
    
    

if __name__ == "__main__":
    demo.launch()