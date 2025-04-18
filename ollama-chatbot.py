from openai import OpenAI
import gradio as gr

#########################################
def chat(message, history):
    #messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    messages = history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
api_key = "ollama"
base_url = "http://127.0.0.1:11434"
MODEL="myllama"
#system_message = "You are a helpful assistant."

openai  = OpenAI(base_url = base_url + "/v1", api_key = api_key)
demo = gr.ChatInterface(fn=chat, type="messages", title="AI Chatbot - " + MODEL + " from " + base_url)
demo.launch()
