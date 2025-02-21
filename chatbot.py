import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

########## Tool ###########
def exchange_rate(foreign_currency):
    print(f"Tool exchange_rate called for {foreign_currency}")
    rates = {"usd": "4016", "cny": "552", "jpy": "26.5"}
    foreign_currency = foreign_currency.lower()
    return rates.get(foreign_currency, "Unknown")

def interest_rate(term):
    print(f"Tool interest_rate called for {term}")
    rates = {"1": "4%", "3": "4.5%", "6": "5%"}
    return rates.get(term, "negotiable at the bank office")

def check_balance_all_accounts(id):
    print(f"Tool check_balance_all_accounts called for {id}")
    total_amount = 0
    try:
        url = "http://127.0.0.1:3000/users/" + id
        response = requests.get(url)
        api_data = response.json()
        accounts = api_data["accounts"]
        number_of_accounts = len(accounts)
        for account in accounts:
            try:
                acct_url = "http://127.0.0.1:3000/accounts/" + account
                acct_response = requests.get(acct_url)
                acct_api_data = acct_response.json()
                amount = acct_api_data["value"]
                total_amount += int(amount)
            except requests.exceptions.Timeout:
                print("timeout when connecting to API server {}".format(acct_url))
    except requests.exceptions.Timeout:
        print("timeout when connecting to API server {}".format(url))
    return total_amount
###############################
def handle_tool_check_balance_all_accounts_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    id = arguments.get("id")
    balance = check_balance_all_accounts(id)
    response = {
        "role": "tool",
        "content": json.dumps({"id": id, "balance": balance}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, id

def handle_tool_exchangerate_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    foreign_currency = arguments.get("foreign_currency")
    rate = exchange_rate(foreign_currency)
    response = {
        "role": "tool",
        "content": json.dumps({"foreign_currency": foreign_currency,"rate": rate}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, foreign_currency

def handle_tool_interestrate_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    term = arguments.get("term")
    rate = interest_rate(term)
    response = {
        "role": "tool",
        "content": json.dumps({"term": term,"rate": rate}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, term
#########################################
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        #print("---------------")
        #print(str(message))
        #print("---------------")

        if "get_exchange_rate" in str(message):
          response, foreign_currency = handle_tool_exchangerate_call(message)
        if "get_interest_rate" in str(message):
          response, term = handle_tool_interestrate_call(message)
        if "check_balance_all" in str(message):
          response, total_amount = handle_tool_check_balance_all_accounts_call(message)
        
        messages.append(message)
        messages.append(response)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

## Main
############### Tools ################
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
    "description": "Get the deposit interest rate for each term (number of month). Call this whenever you need to know the rate, for example when a client asks 'What is the interest rate of 3 months term?'",
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
check_balance_all_accounts_function = {
    "name": "check_balance_all",
    "description": ". Call this whenever you need to know total amount of money that a client has from all of accounts, for example when a client asks 'How much do I have from all accounts?'",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "id of the client, it is the same as the name of the client",
            },
        },
        "required": ["id"],   
        "additionalProperties": False
    }
}
tools = [{"type": "function", "function": exchangerate_function}, {"type": "function", "function": interestrate_function}, {"type": "function", "function": check_balance_all_accounts_function}]
####################################
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
MODEL="gpt-4o"
system_message = "You are a helpful assistant for a bank called Khmer Commercial Bank (KCB)."
system_message += "Here are some quick information about the bank:"
system_message += "Swift code: BKBCKHPP."
system_message += "Address: Daun Penh, Phnom Penh, Cambodia."
system_message += "Establised in 1954, current CEO is Borai Chanto."
system_message += "All of the accounts are in Riel (KHR)."
system_message += "You are talking with a client named Bien. His id in the system is bien."
system_message += "Bien has 2 accounts. The account numbers are 000111 and 000222."
system_message += "His wife is Maya, her id in the bank is maya, her account number is 000333. If he askes to transfer money to his wife, let ask him which account he want to transfer from,"
system_message += " then ask him to confirm the transaction details."
system_message += " If Bien asks to transfer money to account 000444, let stop him because it is a mule account."
system_message += "Finally, refuse to talk about the other topics such as holiday, coding"

openai = OpenAI()
demo = gr.ChatInterface(fn=chat, type="messages", title="AI Chatbot - Personal Banking (using OpenAI with model {})".format(MODEL))
demo.launch()
