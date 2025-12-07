import re
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field,field_validator
from mongodb.item import ItemProductDetails

class ItemProductDetailsResponse(BaseModel):
    items: List[ItemProductDetails] = Field(default=[], alias="items")

# Utility function to clean JSON
def clean_json_response(content: str) -> str:
    """Remove markdown code blocks and extra formatting"""
    # Remove ```json and ``` markers
    content = re.sub(r'```json\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'```\s*', '', content)
    
    # Remove any leading/trailing whitespace
    content = content.strip()
    
    return content

def parse_item_product_details_response(content: str) -> ItemProductDetailsResponse:
        try:
            content = clean_json_response(content)
            product_response = ItemProductDetailsResponse.model_validate_json(content)
            return product_response
        except Exception as e:
            print(f"Validation error: {e}")
            print(f"Response: {content}")
            raise
def save_to_json(data: list[ItemProductDetails]):
    filename = f"enriched_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        # Method 2: Using model_dump() - returns dict
        data_dict = data.model_dump(exclude_none=True,by_alias=True)
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {filename}")

def load_from_json(filename: str) -> ItemProductDetailsResponse:
    """Alternative load method using json.load"""
    with open(filename, 'r', encoding='utf-8') as f:
        # Method 2: Load dict then validate
        data_dict = json.load(f)
        data = ItemProductDetailsResponse.model_validate(data_dict)
    
    print(f"✅ Loaded from {filename}")
    return data