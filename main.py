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

if __name__ == "__main__":
    # Initialize MongoDB client
    mongo_client = MonfoDbClient(uri='mongodb://localhost:27017/', db_name='productDb')
    base_url='https://models.github.ai/inference'
    # api_key=os.environ["GITHUB_TOKEN"]
    api_key=os.environ["OPENAI_API_KEY"]
    
   
    embedding = VectorEmbedding(
        # base_url=base_url,
        api_key=api_key,
        model_name='text-embedding-3-small'
    )
    
    complerer = LLMCompleter(
        # base_url=base_url,
        api_key=api_key,
        model_name='gpt-5-mini',
        embedding = embedding
    ) 
    
    complerer.load_prompt_template(
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md'
    )

    
    # Get the collection
    batchList = mongo_client.load_products_in_batches(batch_size=5,collection_name='ItemDetails',skip=300)
    # Load products in batches
    print("Starting batch processing...")
    for batch in batchList:
        productsBatch = ProductSearchItem()
        for product in batch:
            productsBatch.add_item(product.item_code, product.title)
            parsed_items = productsBatch.get_items_parssed()
        print(f"Processing batch with items: {parsed_items}")
        enriched_text = complerer.erich_text(template_name='batch_product_prompt', text=parsed_items)
        # save_to_json(enriched_text)
        for product,item in zip(batch,enriched_text.items):
            product.sementic_vector = item.sementic_vector
            product.short_description = item.short_description
            product.item_description = item.item_description
            product.item_specification = item.item_specification
            product.search_status = item.search_status
            product.sources = item.sources
            product.tags = item.tags
            product.last_modification = utc_now()
        break
    
        
        mongo_client.insert_products_bulk(collection_name='productEnrichedDb', products_data=[product.model_dump(by_alias=True) for product in batch])
        print("Batch processing completed and saved to database.")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        time.sleep(10)  # To avoid hitting rate limits


    # parsed_items = "UA43J5202ASXMV:TV SAMSUNG LED FHD SMART  43\" | DHU635HZA:HOTTE ASPIRANTE  BOSCH  VISIERE INOX  60CM | 3484B002AA:Canon Cartridge 725 jusqu'a 1600 pages | EB-P1100CSEGWW:ULC Battery Pack [Type-C] Silver | WW-F2S7K:MACHINE A LAVER WESTWING  FRONTALE 7KG 1200T SILVE"
    # print(f"Processing batch with items: {parsed_items}")
    # enriched_text = load_from_json("enriched_products_gpt-4o-mini.json")
    # print(f"Enriched {len(enriched_text.items)} products in batch.")

    # for item in enriched_text.items:
    #     text_to_embed =  concatenate_and_prepare_for_embedding([item.title,item.short_description])
    #     sementic_vector = embedding.get_embedding(text_to_embed)
    #     item.sementic_vector = sementic_vector
    
    # save_to_json(enriched_text)
    # print("Batch processing completed.")
    # Get the first batch from the generator
 
