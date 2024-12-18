import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI


def chat(message, history):
    openai = OpenAI()
    messages = history[:]
    messages.append({"role":"user", "content":message})
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

## Main
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
demo = gr.ChatInterface(fn=chat, type="messages", title="Chat Bot")
demo.launch()
