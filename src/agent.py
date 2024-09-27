from openai import OpenAI
from .query import Query
from .dispatch import Dispatcher
from .hydrate import Hydration
from .models import Response

__all__ = ["Agent"]


class Agent:
    """A class to represent the agent that interacts with the user and remote services."""

    def __init__(self, client: OpenAI):
        """Initializes the Agent object with the provided OpenAI client."""
        self.query = Query(client)
        self.dispatcher = Dispatcher(client)
        self.hydrator = Hydration(client)

    def search(self, query: str) -> Response:
        """Returns a list of Product objects based on the provided query."""

        # 1. Refine the query
        refined_query = self.query.refine(query)

        # 2. Dispatch the refined query to get remote products
        result = self.dispatcher.dispatch(refined_query)

        # 3. Summarize the results
        summary = self.hydrator.summarize(query, result.products)

        # 4. Return the response
        return Response(summary=summary, products=result.products, filters=result.filters)

    def __str__(self):
        return self.__class__.__name__
