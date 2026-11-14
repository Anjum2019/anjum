import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )


    return llm

