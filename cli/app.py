import sys, os
from openai import OpenAI
from .utils import announce, prompt_string
from src import Agent


def main():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        announce("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.", prefix="❌ ")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    agent = Agent(client)

    announce("Welcome to the Shoppy CLI app", prefix="👋 ")

    query = prompt_string("What are you looking for?")

    announce(f"Searching for {query}...", prefix="🔍 ")

    result = agent.search(query)

    if not result:
        announce("No products found. Please try again.", prefix="❌ ")
        sys.exit(1)

    announce("Found the following products:", prefix="🎉 ")
    
    print(f"Summary: {result.summary}")

    for product in result.products:
        print(product)

    sys.exit(0)
