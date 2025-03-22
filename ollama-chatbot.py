import os
from openai import OpenAI
import gradio as gr

#########################################
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
api_key = "ollama"
base_url = "http://192.168.0.2:11434"

MODEL="deepseek-r1:8b"

system_message = ""

openai  = OpenAI(base_url = base_url + "/v1", api_key = api_key)

demo = gr.ChatInterface(fn=chat, type="messages", title="AI Chatbot - Generic")
demo.launch()
