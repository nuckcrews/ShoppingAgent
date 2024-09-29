import sys, os
from datetime import datetime
from openai import OpenAI
from .utils import announce, prompt_string, prompt_confirm
from src import Agent, ProductsResponse


def main():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        announce("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.", prefix="❌ ")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    agent = Agent(client)

    announce("Welcome to the Shoppy CLI app", prefix="👋 ")
    
    while True:
        query = prompt_string("What are you looking for?")
        announce(f"Searching for {query}...", prefix="🔍 ")
        
        # Start timer
        start_time = datetime.now()
        
        # Search
        agent.search(query)
        
        # End timer
        end_timer = datetime.now()
    
        announce(f"\nTotal time taken: {end_timer - start_time}", prefix="⏱️ ")
        
        should_continue = prompt_confirm("Do you want to continue?", default=True)
        
        if not should_continue:
            break

    sys.exit(0)
