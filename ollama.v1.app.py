import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI


def chat(message, history):
    openai = OpenAI()
    messages = history[:]
    messages.append({"role":"user", "content":message})
    response = ollama_via_openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
load_dotenv()
MODEL="llama3.2:latest"
ollama_via_openai = OpenAI(base_url='http://10.8.0.5:11434/v1', api_key='ollama')
demo = gr.ChatInterface(fn=chat, type="messages", title="Chat Bot v1 - Ollama")
demo.launch()

