from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import os

#########################################
def chat(message, history):
#    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    messages = [{"role": "system", "content": system_message}] + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, stream=True)
    partial_message = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        partial_message += delta
        yield partial_message 
    #return response.choices[0].message.content

## Main
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
MODEL="gpt-5.4"

system_message = "You are a helpful assistant."

openai  = OpenAI(base_url = base_url, api_key = api_key)
demo = gr.ChatInterface(fn=chat, title="AI Chatbot - " + MODEL + " from " + base_url)
demo.launch()
