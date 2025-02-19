import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr


########## Tool ###########
def exchange_rate(foreign_currency):
    rates = {"usd": "4016", "cny": "552", "jpy": "26.5"}
    print(f"Tool exchange_rate called for {foreign_currency}")
    foreign_currency = foreign_currency.lower()
    return rates.get(foreign_currency, "Unknown")

def interest_rate(term):
    rates = {"1": "4%", "3": "4.5%", "6": "5%"}
    print(f"Tool interest_rate called for {term}")
    return rates.get(term, "negotiable at the bank office")

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    foreign_currency = arguments.get('foreign_currency')
    rate = exchange_rate(foreign_currency)
    response = {
        "role": "tool",
        "content": json.dumps({"foreign_currency": foreign_currency,"rate": rate}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, foreign_currency


###########################
#def chat(message, history):
#    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
#    response = openai.chat.completions.create(model=MODEL, messages=messages)
#    return response.choices[0].message.content

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, city = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
############### Tool ################
exchangerate_function = {
    "name": "get_exchange_rate",
    "description": "Get the exchange rate between Riel and foreign currencies. Call this whenever you need to know the rate, for example when a client asks 'What is the exchange rate with USD?'",
    "parameters": {
        "type": "object",
        "properties": {
            "foreign_currency": {
                "type": "string",
                "description": "The foreign currency that customer wants to ask for exchange rate",
            },
        },
        "required": ["foreign_currency"],
        "additionalProperties": False
    }
}
interestrate_function = {
    "name": "get_interest_rate",
    "description": "Get the deposit interest rate for each term (number of month). Call this whenever you need to know the rate, for example when a client asks 'What is the interest rate for 3 months?'",
    "parameters": {
        "type": "object",
        "properties": {
            "term": {
                "type": "string",
                "description": "Numer of month (the term) that customer asks for interest rate",
            },
        },
        "required": ["term"],
        "additionalProperties": False
    }
}
tools = [{"type": "function", "function": exchangerate_function}, {"type": "function", "function": interestrate_function}]
####################################
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
MODEL="gpt-4o"

openai = OpenAI()

system_message = "You are a helpful assistant for a bank called Khmer Commercial Bank (KCB)"
system_message += "Here are some quick information about the bank:"
system_message += "Address: Daun Penh, Phnom Penh, Cambodia"
system_message += "Establised in 1954, current CEO is Chea Chanto"
system_message += "You are talking with a client named Bien."
system_message += "Bien has 2 accounts. The account numbers are 000111 and 000222 with the amount of 1000 Riel in each account."
system_message += "His wife account number is 000333. If he askes to transfer money to his wife, let ask him which account he want to transfer from,"
system_message += " then ask him to confirm the transaction details."
system_message += "Finally, refuse to talk about the other topics such as holiday, coding."

demo = gr.ChatInterface(fn=chat, type="messages", title="AI Chatbot - Personal Banking")
demo.launch()
