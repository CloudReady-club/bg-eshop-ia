import os
import logging
import time
from mongodb.mongod import utc_now
from mongodb.mongod import MonfoDbClient
from product.enrich import LLMCompleter
from product.enrich import ProductSearchItem
from product.output import save_to_json, load_from_json

from product.embedding import VectorEmbedding, concatenate_and_prepare_for_embedding

logging.basicConfig(level=logging.INFO)


# Initialize MongoDB client
mongo_client = MonfoDbClient(uri='mongodb://localhost:27017/', db_name='productDb')
base_url='https://models.github.ai/inference'
api_key=os.environ["GITHUB_TOKEN"]

embedding = VectorEmbedding(
    base_url=base_url,
    api_key=api_key,
    model_name='openai/text-embedding-3-small'
)
query_text = "Aspirateur silencieux"
query_embedding = embedding.get_embedding(query_text)
print(f"Query Embedding: {query_embedding[:25]}...")  # Print first 25 dimensions for brevity

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "SementicVector",
            "queryVector": query_embedding,
            "numCandidates": 150,
            "limit": 10,
            "quantization": "scalar"
        }
    },
    {
        "$project": {
            "_id": 0, 
            "ItemCode": 1,
            "Title": 1,
            "ShortDescription": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]
result = mongo_client.aggregate_products(collection_name='productEnrichedDb', pipeline=pipeline)
print("Search Results:")
for doc in result:
    print(doc)