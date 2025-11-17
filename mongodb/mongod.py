from datetime import datetime
from typing import List, Optional, Generator
from pydantic import BaseModel, Field
from pymongo import MongoClient
from mongodb.item import ItemProductDetails

class MonfoDbClient:
    def __init__(self, uri: str = 'mongodb://localhost:27017/', db_name: str = 'your_database'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    
    def load_products_in_batches(self ,collection_name,batch_size=5) -> Generator[List[ItemProductDetails], None, None]:
        """
        Load products in batches using a generator.
        Yields one batch at a time - most memory efficient.
        """
        collection = self.get_collection(collection_name)
        total_count = collection.count_documents({})
        
        skip = 0
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