import os, json
from pydantic import BaseModel
from serpapi import GoogleSearch
from openai import OpenAI
from .models import Product, Filter
from .utils import log, is_debug

__all__ = ["Dispatcher", "RemoteResult"]


class FilteredResult(BaseModel):
    """A class to represent the filtered results from the model."""

    results_positions: list[int]


class RemoteResult(BaseModel):
    """A class to represent the results from the remote service."""

    products: list[Product]
    filters: list[Filter]


class Dispatcher:
    """A class to dispatch queries to remote services."""

    def __init__(self, client: OpenAI):
        """Initializes the Dispatcher object."""

        self.client = client

    def dispatch(self, query: str) -> RemoteResult:
        """Returns a list of filtered results based on the provided query."""

        if is_debug:
            # Extract data from ./resources/example_response.json
            with open("./resources/example_response.json") as f:
                results = json.load(f)
        else:
            # Request SERP API
            params = self._params(query)
            search = GoogleSearch(params)
            results = search.get_json()

        # Extract filters
        filters = self._extract_filters(filters=results.get("filters"))

        # Filter results
        products = self._filter_products(query, results.get("shopping_results"))

        log(lambda: f"Filtered results: {[p.title for p in products]}")
        log(lambda: f"Filter Options: {[f.type for f in filters]}")
        return RemoteResult(products=products, filters=filters)

    def _params(self, query: str) -> dict:
        """Returns the parameters for the remote service based on the provided query."""
        serp_api_key = os.getenv("SERP_API_KEY")

        if not serp_api_key:
            raise ValueError("SERP_API_KEY environment variable is not set.")

        return {
            "api_key": serp_api_key,
            "engine": "google_shopping",
            "q": query,
            "location": "New York, United States",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "direct_link": True,
        }

    def _extract_filters(self, filters: list[dict]) -> list[Filter]:
        """Returns a list of Filter objects based on the provided filters."""

        # If a filter does not have a type, mark it as "default".
        for f in filters:
            if not f.get("type"):
                f["type"] = "default"

        return [Filter(**f) for f in filters]

    def _filter_products(self, query: str, products: list[dict]) -> list[Product]:
        """Returns a list of filtered products based on the provided query and results."""
        
        if not products:
            return []

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful online shopping assistant that breaks down search results to identify the top 5 products based on the user's query and preferences. Please identify the positions of the top 5 products in the search results. Do not let the listed positions influence you.",
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
            response_format=FilteredResult,
        )

        filtered_positions = completion.choices[0].message.parsed.results_positions
        log(lambda: f"Filtered positions: {filtered_positions}")

        if not filtered_positions:
            return []

        refind_results = []
        for position in filtered_positions:
            p = position - 1
            if p >= 0 and p < len(products):
                refind_results.append(Product(**products[p]))

        return refind_results

    def __str__(self):
        return self.__class__.__name__
