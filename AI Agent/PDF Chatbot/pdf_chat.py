# =====================================================
# PDF CHAT ASSISTANT
# LangChain + Chroma + Groq + Gradio
# =====================================================

import gradio as gr
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

# =====================================================
# GLOBAL STATE
# =====================================================

state = {"db": None}

# =====================================================
# MODEL
# =====================================================

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# =====================================================
# PROMPT
# =====================================================

prompt = ChatPromptTemplate.from_messages(
[
    (
        "system",
        """
You are a helpful PDF assistant.

Answer ONLY from the provided context.

Rules:
1. Use only context.
2. If answer does not exist, say:
   "I don't find any answer in the document."
4. Keep answers short and clear.

Context:
{context}
"""
    ),
    ("human", "{question}")
]
)

# =====================================================
# BUILD VECTOR DATABASE
# =====================================================

def build_index(pdf_path):

    pages = PyPDFLoader(pdf_path).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(pages)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./chroma_db"
    )

    return db

# =====================================================
# PDF UPLOAD
# =====================================================
import time
def upload(pdf):

    start = time.time()

    pages = PyPDFLoader(pdf.name).load()



    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(pages)

    

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./chroma_db"
    )

    state["db"] = db

    return f"""
### 📄 Document Information

**File:** `{pdf.name}`

**Pages:** `{len(pages)}`

**Chunks:** `{len(chunks)}`

**Status:** ✅ Ready
"""

# =====================================================
# ASK QUESTION
# =====================================================

def ask(question):

    chunks = state["db"].similarity_search(
        question,
        k=3
    )

    context = "\n\n".join(
        f"[Page {chunk.metadata['page'] + 1}] {chunk.page_content}"
        for chunk in chunks
    )

    chain = prompt | model

    response = chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    return response.content

# =====================================================
# CHAT FUNCTION
# =====================================================

def respond(message, history):

    if history is None:
        history = []

    if state["db"] is None:

       history.append(
            {
                "role": "user",
                "content": message
            })
       history.append(
            {
                "role": "assistant",
                "content": "Please upload a PDF first."
            }
       )
       return "", history

    answer = ask(message)

    history.append(
        {
            "role": "user",
            "content": message
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    print(history)
    
    return "", history

# =====================================================
# CUSTOM CSS
# =====================================================

css = """
body {
    background: linear-gradient(
        135deg,
        #0f172a,
        #1e293b
    ) !important;
}

.gradio-container {
    max-width: 1400px !important;
    background: transparent !important;
}

.dark {
    background: transparent !important;
}

footer {
    display: none !important;
}

/* Chat Area */
.gr-chatbot {
    border-radius: 15px !important;
    border: 1px solid #334155 !important;
}

/* Textbox */
textarea {
    border-radius: 12px !important;
}
#status-box {
    min-height: 250px;
    overflow-y: auto;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 10px;
}

/* Upload Box */
.file-preview {
    border-radius: 15px !important;
}

/* Send Button */
button.primary {
    background: linear-gradient(
135deg,
#111827,
#1f2937
);

    color: white !important;
    font-weight: bold !important;
}

/* Header */
.title {
    font-size: 40px;
    text-align: center;
    font-weight: bold;
    color: white;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 20px;
}
"""

# =====================================================
# UI
# =====================================================

with gr.Blocks(
    title="PDF Chat Assistant",
    css=css
) as demo:

    gr.HTML(
        """
        <div class='title'>
            📄 PDF Chat Assistant
        </div>

        <div class='subtitle'>
            Chat with your PDF using AI + RAG
        </div>
        """
    )

    with gr.Row():

        # LEFT PANEL

        with gr.Column(scale=1):

            pdf = gr.File(
                label="📂 Upload PDF",
                file_types=[".pdf"]
            )

            status = gr.Markdown(
                "No PDF Uploaded",
                elem_id="status-box"
            )

        # RIGHT PANEL

        with gr.Column(scale=3):

            chatbot = gr.Chatbot(
                label="Conversation",
                height=550
            )

            msg = gr.Textbox(
                placeholder="Ask anything about your PDF..."
            )

            send = gr.Button(
                "🚀 Send",
                variant="primary"
            )

    # =====================================
    # EVENTS
    # =====================================

    pdf.upload(
        upload,
        inputs=pdf,
        outputs=status
    )

    send.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

# =====================================================
# START APP
# =====================================================

demo.launch()