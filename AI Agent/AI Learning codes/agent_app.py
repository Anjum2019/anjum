import gradio as gr
from agent_part1 import agent

def chat(message, history):
    return agent(message)
gr.ChatInterface(
    fn=chat,
    title="Smart shopping assistant",
    description="ask me the price of shoes,hat, bag, shorts or pants -i'll look it up"

).launch(share=True)