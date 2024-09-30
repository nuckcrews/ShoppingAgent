from openai import OpenAI
from .dispatch import Dispatcher
from .runner import Runner
from .models import Response, DetailsResponse, ProductsResponse

__all__ = ["Agent"]


class Agent:
    """A class to represent the agent that interacts with the user and remote services."""

    def __init__(
        self,
        client: OpenAI,
        on_product_list: callable,
        on_text_changed: callable,
        thread_id: str = None,
    ):
        """Initializes the Agent object with the provided OpenAI client."""
        self.runner = Runner(client, on_product_list, on_text_changed, thread_id)

    def search(self, input: str) -> Response:
        """The default run execution."""
        self.runner.start(input)

    def __str__(self):
        return self.__class__.__name__
