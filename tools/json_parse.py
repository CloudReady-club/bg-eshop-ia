import json
from typing import List
from pydantic import BaseModel, Field, ValidationError


class Product(BaseModel):
    """Pydantic model for Product items"""
    product_code: str = Field(..., alias="ProductCode")
    name: str = Field(..., alias="Name")
    sub_category_name: str = Field(..., alias="SubCategoryName")
    is_active_item: str = Field(..., alias="IsActiveItem")
    
    class Config:
        populate_by_name = True  # Allow using both snake_case and original names
        
    @property
    def is_active(self) -> bool:
        """Convert string 'True'/'False' to boolean"""
        return self.is_active_item.lower() == 'true'
    
    def to_mongo_doc(self) -> dict:
        """Convert Product to MongoDB document with product_code as _id"""
        doc = self.model_dump(by_alias=True)
        doc['_id'] = doc.pop('ProductCode')
        return doc
    
    @classmethod
    def from_mongo_doc(cls, doc: dict) -> 'Product':
        """Create Product from MongoDB document"""
        if '_id' in doc:
            doc['ProductCode'] = doc.pop('_id')
        return cls(**doc)



def get_product_batch_list(file_path: str,batch_size: int=5) -> List[List[Product]]: 
    prouct_list = _parse_json_file(file_path)
    batches = _batch_products(prouct_list,batch_size)
    return batches

def _parse_json_file(file_path: str) -> List[Product]:
    """
    Parse a JSON file and return a list of Product items with validation.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        List[Product]: List of validated Product objects
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Handle both list and single object
        if isinstance(data, list):
            products = [Product(**item) for item in data]
        elif isinstance(data, dict):
            products = [Product(**data)]
        else:
            raise ValueError("JSON must be an object or array")
            
        return products
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return []
    except ValidationError as e:
        print(f"Error: Validation failed - {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def _batch_products(products: List[Product], batch_size: int) -> List[List[Product]]:
    """
    Split a list of products into batches of specified size.
    
    Args:
        products (List[Product]): List of Product objects
        batch_size (int): Number of items per batch
        
    Returns:
        List[List[Product]]: List of batches, each containing up to batch_size products
    """
    if batch_size <= 0:
        raise ValueError("Batch size must be greater than 0")
    
    batches = []
    for i in range(0, len(products), batch_size):
        batches.append(products[i:i + batch_size])
    
    return batches

