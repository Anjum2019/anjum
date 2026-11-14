from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from scrapper import fetch_website_contents
load_dotenv()

prompt = ChatPromptTemplate.from_template(
    "Give a short, friendly summary of this website:\n\n{website}"
)
model = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model= "openai/gpt-oss-20b", 
    temperature=0.3)
parser = StrOutputParser() #takes that raw response and extracts just the plain text string.

#Input goes into the prompt → formatted text.| That text flows into the model → AI generates a reply. | The reply flows into the parser → clean string output.
chain = prompt | model | parser 

def summarizer(url):
    return chain.invoke({"website": fetch_website_contents(url)})
print(summarizer("https://anthropic.com"))