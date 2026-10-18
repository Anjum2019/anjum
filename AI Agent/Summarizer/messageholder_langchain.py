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

history = [HumanMessage("My name is Anjum."), AIMessage("Hi Anjum!")]
print(chain.invoke({"history":history,"question":"What is my name?"}).content)
