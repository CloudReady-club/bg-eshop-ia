import os
import logging
from mongodb.item import ItemProductDetails
from mongodb.mongod import MonfoDbClient
from product.enrich import LLMCompleter
from product.enrich import ProductSerchItem

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Initialize MongoDB client
    mongo_client = MonfoDbClient(uri='mongodb://localhost:27017/', db_name='productDb')
    complerer = LLMCompleter(
        base_url='https://models.github.ai/inference',
        api_key=os.environ["GITHUB_TOKEN"],
        model_name='xai/grok-3'
    )  
    
    complerer.load_prompt_template(
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md'
    )
    # Get the collection
    batchList = mongo_client.load_products_in_batches(batch_size=2,collection_name='ItemDetails')
    # Load products in batches
    print("Starting batch processing...")
    for batch in batchList:
        productsBatch = ProductSerchItem()
        for product in batch:
            productsBatch.add_item(product.item_code, product.title)
          
        parsed_items = productsBatch.get_items_parssed()
        print(f"Processing batch with items: {parsed_items}")
        enriched_text = complerer.erich_text(template_name='batch_product_prompt', text=parsed_items)
        print(f"Enriched batch response: {enriched_text}")   
        
       
     