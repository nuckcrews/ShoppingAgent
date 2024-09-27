from openai import OpenAI
from .models import Product

__all__ = ["Hydration"]


class Hydration:
    """A class to hydrate product lists with additional information."""

    def __init__(self, client: OpenAI):
        """Initializes the Hydration object with the provided OpenAI client."""
        self.client = client

    def summarize(self, query: str, products: list[Product]) -> str:
        """Returns a summary of the provided list of Product objects."""

        # Summarize the results
        summary = self._summarize(query, products)

        return summary

    def _summarize(self, query: str, products: list[Product]) -> str:
        """Returns a summary of the provided list of Product objects."""

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful online shopping assistant that summarizes the search results for a given query and provides a reccomendation. Keep the summary short, concise and informative.",
                },
                {
                    "role": "user", 
                    "content": f"Query: {query}"
                },
                {
                    "role": "user", 
                    "content": f"Results: {products}"
                },
            ],
        )

        return completion.choices[0].message.content.strip()
