import os
import logging
import time
from mongodb.mongod import utc_now
from mongodb.mongod import MonfoDbClient
from product.enrich import LLMCompleter
from product.enrich import ProductSearchItem
from product.output import save_to_json, load_from_json



logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Initialize MongoDB client
    mongo_client = MonfoDbClient(uri='mongodb://localhost:27017/', db_name='productDb')
    base_url='https://models.github.ai/inference'
    api_key=os.environ["GITHUB_TOKEN"]
  

    
    complerer = LLMCompleter(
        base_url=base_url,
        api_key=api_key,
        model_name='gpt-4o',
        embedding_model_name='openai/text-embedding-3-small',
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md'
    ) 
    


    i=0
    # Get the collection
    batchList = mongo_client.load_products_in_batches(batch_size=5,collection_name='ItemDetails',skip=450)
    # Load products in batches
    print("Starting batch processing...")
    for batch in batchList:
        i= i+1
        batch = complerer.process_products_enrichment(products=batch)
        mongo_client.insert_products_bulk(collection_name='productEnrichedDb', products_data=[product.model_dump(by_alias=True) for product in batch])
        print("Batch processing completed and saved to database.")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        time.sleep(5)  # To avoid hitting rate limits
        if i>=5:
            break

 
