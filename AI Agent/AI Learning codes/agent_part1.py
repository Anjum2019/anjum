import json
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PRICES = {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699}

def get_price(item):
    print(f"🔧 tool calles: get_price({item})")
    return f"₹{PRICES.get(item.lower(),'unknown')}"

tools = [{
    "type": "function",
    "function": {
        "name": "get_price",
        "descritpion": "Get the price of a shop item the user asks about.",
        "parameters": {
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]
def agent(user_message):
    messages = [{"role": "user","content": user_message}]
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", messages = messages, tools = tools)
    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = get_price(args["item"])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", messages = messages)
        msg = response.choices[0].message

    return msg.content
print(agent("how much are the hat?"))
print(agent("hi! Waht can you help with?"))