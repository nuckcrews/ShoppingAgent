import os

__all__ = ["is_debug", "log"]

is_debug = os.getenv("ENV") != "production"

# a logging method that only executes the message closure if it's debug mode
def log(message_callable: callable):
    if is_debug:
        print(message_callable())
    