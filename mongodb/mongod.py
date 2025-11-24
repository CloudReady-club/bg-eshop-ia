from datetime import datetime
from typing import List, Optional, Generator
from pydantic import BaseModel, Field
from pymongo import MongoClient
from mongodb.item import ItemProductDetails
from datetime import timezone

class MongoDbClient:
    def __init__(self, uri: str = 'mongodb://localhost:27017/', db_name: str = 'your_database'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    
    def load_products_in_batches(self ,collection_name,batch_size=5,skip = 0) -> Generator[List[ItemProductDetails], None, None]:
        """
        Load products in batches using a generator.
        Yields one batch at a time - most memory efficient.
        """
        collection = self.get_collection(collection_name)
        total_count = collection.count_documents({})
        
       
        while skip < total_count:
            # Fetch batch
            documents = list(collection.find().skip(skip).limit(batch_size))
            
            # If no more documents, stop
            if not documents:
                break
            
            # Convert to Pydantic models
            batch = []
            for doc in documents:
                try:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    product = ItemProductDetails(**doc)
                    batch.append(product)
                except Exception as e:
                    print(f"Error loading document {doc.get('_id')}: {e}")
                    continue
            
            # Yield the batch
            yield batch
            skip += batch_size

    
    def insert_product(self, collection_name: str, product_data: dict) -> str:
        collection = self.get_collection(collection_name)
        result = collection.insert_one(product_data)
        return str(result.inserted_id)
    
    def update_product(self, collection_name: str, product_id: str, update_data: dict) -> bool:
        collection = self.get_collection(collection_name)
        result = collection.update_one({'_id': product_id}, {'$set': update_data})
        return result.modified_count > 0
    
    def delete_product(self, collection_name: str, product_id: str) -> bool:
        collection = self.get_collection(collection_name)
        result = collection.delete_one({'_id': product_id})
        return result.deleted_count > 0
    
    def get_product_by_id(self, collection_name: str, product_id: str) -> Optional[ItemProductDetails]:
        collection = self.get_collection(collection_name)
        document = collection.find_one({'_id': product_id})
        if document:
            if '_id' in document:
                document['_id'] = str(document['_id'])
            return ItemProductDetails(**document)
        return None 
    
    def insert_products_bulk(self, collection_name: str, products_data: List[dict]) -> List[str]:
        collection = self.get_collection(collection_name)
        result = collection.insert_many(products_data)
        return [str(inserted_id) for inserted_id in result.inserted_ids]
    def aggregate_products(self, collection_name: str, pipeline: List[dict]) -> List[dict]:
        collection = self.get_collection(collection_name)
        results = list(collection.aggregate(pipeline))
        return results
    
    def close(self):
        self.client.close()

def utc_now() -> datetime:
        return datetime.now(timezone.utc)