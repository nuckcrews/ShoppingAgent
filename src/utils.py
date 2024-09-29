import os, re

__all__ = ["is_debug", "log", "remove_links"]

is_debug = os.getenv("ENV") != "production"

# a logging method that only executes the message closure if it's debug mode
def log(message_callable: callable):
    if is_debug:
        print(message_callable(), flush=True)
    
def remove_links(input):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return re.sub(url_pattern, '<LINK>', input)