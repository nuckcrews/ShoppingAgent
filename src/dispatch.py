import os, json, asyncio
from urllib.parse import urlparse
from urllib.parse import parse_qs
from pydantic import BaseModel
from serpapi import GoogleSearch
from .models import Filter
from .error import NoResultsError
from .utils import log, is_debug

__all__ = ["Dispatcher", "RemoteResult", "SearchQuery"]


class FilteredResult(BaseModel):
    """A class to represent the filtered results from the model."""

    results_positions: list[int]


class RemoteResult(BaseModel):
    """A class to represent the results from the remote service."""

    id: str
    query: str
    products: list[dict]
    filters: list[Filter]
    
    def to_string(self):
        model = self.model_dump()
        # remove id
        model.pop("id")
        return json.dumps(model)

class SearchQuery(BaseModel):
    
    id: str
    text: str

class Dispatcher:
    """A class to dispatch queries to remote services."""

    def __init__(self):
        """Initializes the Dispatcher object."""
        pass 

    def search(self, queries: list[SearchQuery]) -> list[RemoteResult]:
        """Returns a list of filtered results based on the provided query."""

        async def _search(query: SearchQuery) -> RemoteResult:
            # Get search parameters
            params = self._search_params(query=query.text)

            # Dispatch the search
            results = await asyncio.to_thread(self._dispatch, params)

            # Extract filters
            filters = self._extract_filters(filters=results.get("filters"))

            # Extract results
            products = self._extract_products(products=results.get("shopping_results"))

            log(lambda: f"Extracted results: {[p.get('title') for p in products]}")
            log(lambda: f"Filter Options: {[f.type for f in filters]}")
            return RemoteResult(id=query.id, query=query.text, products=products, filters=filters)
        
        async def _run_searches():
            return await asyncio.gather(*[_search(query) for query in queries])

        # Run the searches in parallel
        results = asyncio.run(_run_searches())
        return results

    def filter(self, link: str) -> RemoteResult:
        """Returns a list of filtered results based on the provided link."""

        # Extract params from link (its a url)
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        params_dict = {k: v[0] for k, v in params.items()}
        
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            raise ValueError("SERP_API_KEY environment variable is not set.")

        params_dict["api_key"] = serp_api_key

        # Dispatch the search
        results = self._dispatch(params=params_dict)

        # Extract filters
        filters = self._extract_filters(filters=results.get("filters"))

        # Extract results
        products = self._extract_products(products=results.get("shopping_results"))

        log(lambda: f"Extracted results: {[p.get("title") for p in products]}")
        log(lambda: f"Filter Options: {[f.type for f in filters]}")
        return RemoteResult(id="", query=link, products=products, filters=filters)

    def details(self, link: str) -> dict:
        """Returns a list of filtered results based on the provided link."""

        # Extract params from link (its a url)
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        params_dict = {k: v[0] for k, v in params.items()}
        
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            raise ValueError("SERP_API_KEY environment variable is not set.")

        params_dict["api_key"] = serp_api_key

        # Dispatch the search
        results = self._dispatch(params=params_dict)
        
        # Remove unnecessary fields
        results.pop("search_parameters", None)
        results.pop("search_metadata", None)

        log(lambda: f"Extracted results: {results.get('product_results').get("title")}")
        # Extract results
        return results

    def _dispatch(self, params: dict) -> dict:
        """Dispatches the provided parameters to the remote service."""

        if is_debug:
            # Extract data from ./resources/example_response.json
            with open("./resources/example_response.json") as f:
                results = json.load(f)
        else:
            # Request SERP API
            search = GoogleSearch(params)
            results = search.get_json()

        error = results.get("error")
        if error:
            raise NoResultsError(error)

        return results

    def _search_params(self, query: str) -> dict:
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
            "direct_link": "true",
        }

    def _extract_filters(self, filters: list[dict]) -> list[Filter]:
        """Returns a list of Filter objects based on the provided filters."""

        # If a filter does not have a type, mark it as "default".
        for f in filters:
            if not f.get("type"):
                f["type"] = "default"

        return [Filter(**f) for f in filters]

    def _extract_products(self, products: list[dict]) -> list[dict]:
        """Returns a list of the top 10 Product objects based on the provided products."""

        if not products:
            return []

        return products[:10]

    def __str__(self):
        return self.__class__.__name__
