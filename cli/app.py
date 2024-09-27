import sys, os
from datetime import datetime
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

    # Start timer
    start_time = datetime.now()
    
    # Search
    result = agent.search(query)
    
    # End timer
    end_timer = datetime.now()

    if not result:
        announce("\nNo products found. Please try again.", prefix="❌ ")
        sys.exit(1)

    announce("\nFound the following products:", prefix="🎉 ")
    
    print(f"Summary:\n{result.summary}")
    
    print("\nProducts:")
    for product in result.products:
        print(f"{product}\n")
        
    announce(f"Total time taken: {end_timer - start_time}", prefix="⏱️ ")

    sys.exit(0)
