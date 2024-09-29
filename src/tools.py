def instructions():
    return "You are a highly intelligent shopping assistant who helps users find products they love. You can search for products by using Google search. Identify what the user wants and search for products using queries that you think will work best. If the user has a question about a specific product, gather information about the product and answer them as well as you can. Help the user make a purchasing decision."

def execute_search():
    return {
        "name": "execute_search",
        "description": "Search for products based on the provided query.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for products.",
                }
            },
            "additionalProperties": False,
            "required": ["query"],
        },
    }


def product_detailts():
    return {
        "name": "get_product_details",
        "description": "Get details for a specific product based on the provided serp api product link.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "serpapi_product_api": {
                    "type": "string",
                    "description": "The serpapi product api link to get details for.",
                }
            },
            "additionalProperties": False,
            "required": ["serpapi_product_api"],
        },
    }


def filter():
    return {
        "name": "filter_results",
        "description": "Filter the search results based on the provided serp api link.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "serpapi_link": {
                    "type": "string",
                    "description": "The serpapi filter link to get results for.",
                }
            },
            "additionalProperties": False,
            "required": ["serpapi_link"],
        },
    }
