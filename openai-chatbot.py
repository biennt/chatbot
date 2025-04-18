import os
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr

#########################################
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
MODEL="gpt-4o"
system_message = "You are F5 Solutions Engineer who provides consultation and support to customers."

openai  = OpenAI()
demo = gr.ChatInterface(fn=chat, type="messages", title="AI Chatbot - " + MODEL)
demo.launch()
