from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

# Step 5: Open the same Vector store as built in step 1
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedder)
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

# Step 6: the prompt = instructions + chunks + question
prompt = ChatPromptTemplate.from_template("""
Ansewer the Question using only the context below. If the context doesn't contain the answer, say "I don't know". Be concise and quote facts directly.

cotenxt: {context}

Question: {question}
""")

def rag_answer(question):
    chunks = db.similarity_search(question, k=3)
    context = "\n\n".join(c.page_content for c in chunks)
    chain = prompt | model
    return chain.invoke({"context": context, "question": question}).content

print(rag_answer("how long do i have to return something?"))
