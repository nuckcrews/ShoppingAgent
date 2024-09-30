import json
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
from openai.types.beta.threads import Message, MessageDelta
from openai.types.beta.threads.runs import ToolCall, RunStep
from openai.types.beta import AssistantStreamEvent
from .dispatch import Dispatcher, SearchQuery
from .utils import log

__all__ = ["Runner"]


class Runner:

    _assistant_id = "asst_0ikYWUWwI9pm3wyousqovlNp"

    def __init__(
        self,
        client: OpenAI,
        on_product_list: callable,
        on_text_changed: callable,
        thread_id: str = None,
    ):
        self.client = client
        self.dispatcher = Dispatcher()
        self.on_product_list = on_product_list
        self.on_text_changed = on_text_changed
        if not thread_id:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
        else:
            self.thread_id = thread_id

    def start(self, query: str) -> None:
        """Runs the assistant with the provided query."""

        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=[
                {
                    "type": "text",
                    "text": query,
                },
            ],
        )

        event_handler = EventHandler(
            client=self.client, 
            dispatcher=self.dispatcher, 
            thread_id=self.thread_id,
            on_product_list=self.on_product_list,
            on_text_changed=self.on_text_changed,
        )

        # Create a new run
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self._assistant_id,
            event_handler=event_handler,
            parallel_tool_calls=True,
        ) as stream:
            stream.until_done()

        return


class EventHandler(AssistantEventHandler):
    """A class to handle assistant events."""

    def __init__(
        self,
        client: OpenAI,
        dispatcher: Dispatcher,
        thread_id: str,
        on_product_list: callable,
        on_text_changed: callable,
    ):
        super().__init__()
        self.client = client
        self.dispatcher = dispatcher
        self.thread_id = thread_id
        self.run_id = None
        self.run_step = None
        self.non_search_tool_calls: list[ToolCall] = []
        self.search_tool_calls: list[ToolCall] = []
        self.on_product_list = on_product_list
        self.on_text_changed = on_text_changed

    @override
    def on_end(self):
        log(lambda: f"\n end assistant > {self.current_run_step_snapshot}")
        return super().on_end()

    @override
    def on_exception(self, exception: Exception) -> None:
        """Fired whenever an exception happens during streaming"""
        log(lambda: f"\nassistant > {exception}\n")
        return super().on_exception(exception)

    @override
    def on_tool_call_created(self, tool_call):
        log(lambda: f"\nassistant on_tool_call_created > {tool_call}")
        return super().on_tool_call_created(tool_call)

    @override
    def on_tool_call_done(self, tool_call: ToolCall) -> None:
        log(lambda: f"\nassistant on_tool_call_done > {tool_call}")
        keep_retrieving_run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id, run_id=self.run_id
        )

        log(lambda: f"\run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            return

        elif keep_retrieving_run.status == "in_progress":

            if tool_call.function.name == "execute_search":
                self.search_tool_calls.append(tool_call)
            else:
                self.non_search_tool_calls.append(tool_call)

        elif keep_retrieving_run.status == "requires_action":
            if tool_call.function.name == "execute_search":
                self.search_tool_calls.append(tool_call)
            else:
                self.non_search_tool_calls.append(tool_call)

            tool_outputs = []

            queries: list[SearchQuery] = []
            for tool_call in self.search_tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if name == "execute_search":
                    query = arguments.get("query")
                    if not query:
                        raise ValueError("No query provided to search")

                    queries.append(SearchQuery(id=tool_call.id, text=query))

            if len(queries) > 0:
                search_results = self.dispatcher.search(queries)

                for result in search_results:
                    tool_outputs.append(
                        {
                            "tool_call_id": result.id,
                            "output": result.to_string(),
                        }
                    )
                    self.on_product_list(result.products)

            for tool_call in self.non_search_tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if name == "filter_results":
                    link = arguments.get("serpapi_link")
                    if not link:
                        raise ValueError("No link provided to filter")

                    filter_results = self.dispatcher.filter(link)

                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.id,
                            "output": filter_results.to_string(),
                        }
                    )

                    self.on_product_list(filter_results.products)

                elif name == "get_product_details":
                    link = arguments.get("serpapi_product_api")
                    if not link:
                        raise ValueError("No link provided to get product details")

                    product_details = self.dispatcher.details(link)

                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(product_details),
                        }
                    )

                    self.on_product_list([product_details])

            event_handler = EventHandler(
                client=self.client,
                dispatcher=self.dispatcher,
                thread_id=self.thread_id,
                on_product_list=self.on_product_list,
                on_text_changed=self.on_text_changed,
            )

            with self.client.beta.threads.runs.submit_tool_outputs_stream(
                run_id=self.run_id,
                thread_id=self.thread_id,
                tool_outputs=tool_outputs,
                event_handler=event_handler,
            ) as stream:
                stream.until_done()

        return super().on_tool_call_done(tool_call)

    @override
    def on_run_step_created(self, run_step: RunStep) -> None:
        log(lambda: f"on_run_step_created")
        self.run_id = run_step.run_id
        self.run_step = run_step
        log(lambda: f"The type of run_step run step is {type(run_step)}")
        log(lambda: f"\n run step created assistant > {run_step}\n")
        return super().on_run_step_created(run_step)

    @override
    def on_run_step_done(self, run_step: RunStep) -> None:
        log(lambda: f"\n run step done assistant > {run_step.id}\n")
        return super().on_run_step_done(run_step)

    # MARK - Message and text events

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        self.on_text_changed(delta.value)
        return super().on_text_delta(delta, snapshot)

    @override
    def on_message_delta(self, delta: MessageDelta, snapshot: Message) -> None:
        return super().on_message_delta(delta, snapshot)

    @override
    def on_message_created(self, message: Message) -> None:
        log(lambda: f"\nassistant on_message_created > {message}\n")
        return super().on_message_created(message)

    @override
    def on_message_done(self, message: Message) -> None:
        log(lambda: f"\nassistant on_message_done > {message}\n")
        return super().on_message_done(message)
