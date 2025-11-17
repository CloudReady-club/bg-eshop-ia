from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field,field_validator

class Paragraph(BaseModel):
    title: Optional[str] = Field(default=None, alias="Title")
    text: Optional[str] = Field(default=None, alias="Text")

class ItemDescription(BaseModel):
    paragraphs: List[Paragraph] = Field(default=[], alias="Paragraphs")

class Specification(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    value: Optional[str] = Field(default=None, alias="Value")

class SpecificationCategory(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    specifications: List[Specification] = Field(default=[], alias="Specifications")

class ItemSpecification(BaseModel):
    specification_categories: List[SpecificationCategory] = Field(default=[], alias="SpecificationCategories")

# class ItemPicture(BaseModel):
#     title: Optional[str] = None
#     picture_url: Optional[str] = None
#     picture_miniature_url: Optional[str] = None
#     main_picture: bool = False

class ItemProductDetails(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    item_code: Optional[str] = Field(default=None, alias="ItemCode")
    title: Optional[str] = Field(default=None, alias="Title")
    short_description: Optional[str] = Field(default=None, alias="ShortDescription")
    item_description: Optional[ItemDescription] = Field(default=None, alias="ItemDescription")
    item_specification: Optional[ItemSpecification] = Field(default=None, alias="ItemSpecification")
    # item_pictures: List[ItemPicture] = Field(default=[], alias="ItemPicture")
    last_modification: datetime = Field(default=None, alias="LastModification")

    @field_validator('last_modification', mode='before')
    @classmethod
    def parse_mongo_date(cls, v):
        if isinstance(v, dict) and '$date' in v:
            # Parse ISO format string to datetime
            return datetime.fromisoformat(v['$date'].replace('Z', '+00:00'))
        return v
    
    class Config:
        populate_by_name = True


