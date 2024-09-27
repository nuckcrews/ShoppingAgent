from openai import OpenAI
from .utils import log

__all__ = ["Query"]


class Query:
    """A class to parse queries and refine product lists."""

    def __init__(self, client: OpenAI):
        """Initializes the Parser object with the provided OpenAI client."""
        self.client = client

    def refine(self, query: str) -> str:
        """Refines the provided query in preparation for product search."""

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful online shopping assistant that breaks down complex queries into simple ones. Take a user search query and convert it into a perfect google search that captures exactly what the user is looking for.",
                },
                {
                    "role": "user", 
                    "content": query
                },
            ]
        )

        refined_query = completion.choices[0].message.content.strip()

        if not refined_query:
            refined_query = query

        log(lambda: f"Refined query: {refined_query}")
        return refined_query

    def __str__(self):
        return self.__class__.__name__
