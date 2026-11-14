import os
from openai import OpenAI
# pip install openai - this installation is required to use the OpenAI-compatible SDK for Groq
# pip install python-dotenv - this installation is required to load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()    # loads everything from .env

# reads your API key from the environment
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model ="openai/gpt-oss-20b",                           
    messages=[
        {"role": "system", "content": "You are a witty travel guide"},
        {"role": "user", "content": "Suggest one thing to do in Bangalore."},
    ],
)
print(response.choices[0].message.content)

# now OpenAI() finds the key automatically — no key in your code 🎉

# --------------------------------------------------------------------------------------------------
# import os
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load variables from .env
# load_dotenv()

# # Read your Groq API key
# api_key = os.getenv("GROQ_API_KEY")

# if not api_key:
#     raise ValueError(
#         "GROQ_API_KEY not found. Check your .env file."
#     )

# # Connect to Groq using the OpenAI-compatible SDK
# client = OpenAI(
#     api_key=api_key,
#     base_url="https://api.groq.com/openai/v1",
# )

# # Send a message to the model
# response = client.chat.completions.create(
#     model="openai/gpt-oss-20b",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a witty travel guide."
#         },
#         {
#             "role": "user",
#             "content": "Suggest one thing to do in Bangalore."
#         },
#     ],
# )

# # Print the AI's response
# print(response.choices[0].message.content)
