from typing import Optional
from pydantic import BaseModel

__all__ = ["Product", "Filter", "Response"]


class Product(BaseModel):
    """A class to represent a product."""

    title: str
    link: str
    product_link: str
    product_id: str
    price: str
    extracted_price: float
    source: str
    source_icon: str
    thumbnail: str
    delivery: Optional[str] = None
    extensions: Optional[list[str]] = None
    tag: Optional[str] = None
    serpapi_product_api: str
    old_price: Optional[str] = None
    extracted_old_price: Optional[float] = None
    snippet: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None


class Filter(BaseModel):
    """A class to represent a filter."""

    type: str
    options: list[dict]


class Response(BaseModel):
    """A class to represent the agent response."""

    summary: str
    products: list[Product]
    filters: list[Filter]
