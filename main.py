import os
import logging
from mongodb.item import ItemProductDetails
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
    api_key=os.environ["GITHUB_TOKEN"]

    complerer = LLMCompleter(
        base_url=base_url,
        api_key=api_key,
        model_name='gpt-4o-mini'
    )  
    
    complerer.load_prompt_template(
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md'
    )

    embedding = VectorEmbedding(
        base_url=base_url,
        api_key=api_key,
        model_name='openai/text-embedding-3-small'
    )
    # Get the collection
    batchList = mongo_client.load_products_in_batches(batch_size=5,collection_name='ItemDetails')
    # Load products in batches
    print("Starting batch processing...")
    # for batch in batchList:
    #     productsBatch = ProductSearchItem()
    #     for product in batch:
    #         productsBatch.add_item(product.item_code, product.title)
    #         parsed_items = productsBatch.get_items_parssed()
    #     print(f"Processing batch with items: {parsed_items}")
    #     enriched_text = complerer.erich_text(template_name='batch_product_prompt', text=parsed_items)
    #     save_to_json(enriched_text)
    #     break


    parsed_items = "UA43J5202ASXMV:TV SAMSUNG LED FHD SMART  43\" | DHU635HZA:HOTTE ASPIRANTE  BOSCH  VISIERE INOX  60CM | 3484B002AA:Canon Cartridge 725 jusqu'a 1600 pages | EB-P1100CSEGWW:ULC Battery Pack [Type-C] Silver | WW-F2S7K:MACHINE A LAVER WESTWING  FRONTALE 7KG 1200T SILVE"
    print(f"Processing batch with items: {parsed_items}")
    enriched_text = load_from_json("enriched_products_gpt-4o-mini.json")
    print(f"Enriched {len(enriched_text.items)} products in batch.")

    for item in enriched_text.items:
        text_to_embed =  concatenate_and_prepare_for_embedding([item.title,item.short_description])
        sementic_vector = embedding.get_embedding(text_to_embed)
        item.sementic_vector = sementic_vector
    
    save_to_json(enriched_text)
    print("Batch processing completed.")
      
        

          
        
       
     