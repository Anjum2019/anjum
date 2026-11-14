from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

# Define the model
model = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model= "openai/gpt-oss-20b", 
    temperature=0.3)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly tytor."),
        MessagesPlaceholder("history"),
        ("human","{question}"),
    ]
)

chain = prompt | model

history = []

print("chat with the bot (type 'quite' to exit).")
while True:
    question = input("you:")
    if question.strip().lower() in {"quite","exit"}:
        break

    answer = chain.invoke(
        {"history":history,"question":question}).content

    print("bot:",answer)
    history.append(HumanMessage(question))
    history.append(AIMessage(answer))
    print(f" (history now has {len(history)} messages)")