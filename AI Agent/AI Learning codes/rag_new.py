from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

# Step 5: Open the same Vector store as built in step 1
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedder)
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

prompt= ChatPromptTemplate.from_messages(
    [
        ("system", """
        You are a chatbot.
        Answer the question using only the context below.
        Context:
        {context}
        If the context doesn't contain the answer,
        say 'I don't know'.
        Be concise and quote facts directly."""),
        MessagesPlaceholder("history"),
        ("human","{question}"),
    ])

chain = prompt | model

history = []  #history = [] is used to store previous HumanMessage and AIMessage objects

while True:
    question = input("You: ")

    if question.strip().lower() in {"quit", "exit"}:
        break

    chunks = db.similarity_search(question, k=3)
    context = "\n\n".join(c.page_content for c in chunks)

    answer = chain.invoke({
        "context": context,
        "history": history,
        "question": question
    }).content

    print("Bot:", answer)

    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=answer))

    print(f"(history now has {len(history)} messages)")