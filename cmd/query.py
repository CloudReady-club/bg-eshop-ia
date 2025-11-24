from pydantic import BaseModel
from typing import List


class ProductInput(BaseModel):
    item_code: str
    title: str


class SearchRequest(BaseModel):
    products: List[ProductInput]


