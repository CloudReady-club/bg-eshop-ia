from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field,field_validator
from mongodb.item import ItemProductDetails

class ItemProductDetailsResponse(BaseModel):
    items: List[ItemProductDetails] = Field(default=[], alias="items")