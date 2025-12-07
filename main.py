import os
import logging
import time
from pathlib import Path
from mongodb.mongod import utc_now
from mongodb.mongod import MongoDbClient
from product.enrich import LLMCompleter
from product.enrich import ProductSearchItem
from product.output import save_to_json, load_from_json,ItemProductDetailsResponse
from tools.json_parse import get_product_batch_list



logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Initialize MongoDB client
    mongo_client = MongoDbClient(uri='mongodb://localhost:27017/', db_name='productDb')
    base_url='https://bg-ehop-resource.openai.azure.com/openai/v1/'
    api_key=os.environ["GITHUB_TOKEN"]
    
    # # Display the data to be analyzed
    script_dir = Path(__file__).parent  # Get the directory of the script


    
    complerer = LLMCompleter(
        base_url=base_url,
        api_key=api_key,
        model_name='grok-3-mini',
        embedding_model_name='openai/text-embedding-3-small',
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md'
    ) 

    file_path = script_dir / 'tv_list.json'
    proudct_list = get_product_batch_list(file_path)
    product_code_list = [product.product_code for product in proudct_list[0]]
    batchList = mongo_client.fetch_products_by_batch(collection_name='ItemDetails',product_codes=product_code_list)

    batchList = complerer.process_products_enrichment(products=batchList)
  
    mongo_client.insert_products_bulk(collection_name='productEnrichedDb', products_data=[product.model_dump(by_alias=True) for product in batchList])

    


    # i=0
    # # Get the collection
    # batchList = mongo_client.load_products_in_batches(batch_size=5,collection_name='ItemDetails',skip=450)
    # # Load products in batches
    # print("Starting batch processing...")
    # for batch in batchList:
    #     i= i+1
    #     batch = complerer.process_products_enrichment(products=batch)
    #     mongo_client.insert_products_bulk(collection_name='productEnrichedDb', products_data=[product.model_dump(by_alias=True) for product in batch])
    #     print("Batch processing completed and saved to database.")
    #     print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    #     time.sleep(5)  # To avoid hitting rate limits
    #     if i>=5:
    #         break

 
