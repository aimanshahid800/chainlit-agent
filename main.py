import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI-API-KEY")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Agent
greeting_agent = Agent(
    model=model,
    instructions="You are a smart, friendly, and professional AI assistant. Always provide helpful, accurate, and detailed answers in simple, easy-to-understand language. Keep your tone warm, respectful, and supportive. If a user is confused, try to explain step by step. When appropriate, include examples, code snippets, or references from reputable sources. If you don’t know something, be honest and guide the user to the right direction.",
    name="greeting_agent"
)

# Chainlit provide history of messages


@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])


@cl.on_message  # decorator function
async def main(message: cl.Message):

    # Show something on the screen
    msg = cl.Message(
        content="",
    )
    await msg.send()

    # Step 1:
    print("\nStep 1:Get History and add User Message\n")
    history = cl.user_session.get("history")  # [...]
    print("History: ", history)
    print("\nStep 2: Add User Messaged to History\n")
    history.append({"role": "user", "content": message.content})  # [{}]
    print("Updated History: ", history)

    # Agent Call
    agent_response = Runner.run_streamed(greeting_agent, history)
    async for event in agent_response.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            raw_text = event.data.delta
            await msg.stream_token(raw_text)

    # msg.content = agent_response.final_output
    # await msg.update()

    # Step 2:
    # Get History and add Agent Message
    print("\nStep 3: Get History and add Agent Message\n")
    history.append(
        {"role": "assistant", "content": agent_response.final_output})
    # Step 3:
    # Update History
    print("\nStep 4: Update History\n")
    cl.user_session.set("history", history)