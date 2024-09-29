from typing import Optional
from pydantic import BaseModel
from enum import Enum

__all__ = [
    "Product",
    "Filter",
    "Response",
    "ResponseType",
    "ProductsResponse",
    "DetailsResponse",
    "CompareResponse",
    "TextResponse",
    "ErrorResponse",
]


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


class ResponseType(str, Enum):
    products = "products"
    details = "details"
    compare = "compare"
    text = "text"
    error = "error"


class ResponseModel(BaseModel):
    pass


class ErrorResponse(ResponseModel):

    message: str


class ProductsResponse(ResponseModel):

    text: str
    products: list[dict]
    filters: list[Filter]


class DetailsResponse(ResponseModel):

    text: str
    product: dict


class CompareResponse(ResponseModel):

    text: str
    products: list[dict]


class TextResponse(ResponseModel):

    text: str


class Response(BaseModel):

    type: ResponseType
    model: ResponseModel
