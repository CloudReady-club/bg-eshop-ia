# app.py

import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from fastapi import FastAPI, HTTPException
from product.enrich import LLMCompleter, ProductSearchItem
from cmd.query import SearchRequest
from product.output import ItemProductDetailsResponse
app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.post("/enrich_product", response_model=ItemProductDetailsResponse)
def enrich(req: SearchRequest):
    if req is None or not req.products:
        raise HTTPException(status_code=400, detail="No products provided for enrichment")
    if req.products is None or len(req.products) == 0:
        raise HTTPException(status_code=400, detail="Product list is empty")
    if req.products and len(req.products) > 5:
        raise HTTPException(status_code=400, detail="Too many products provided. Maximum allowed is 100.")
    
 
    base_url='https://models.github.ai/inference'
    api_key = os.environ.get("GITHUB_TOKEN")
    if not api_key:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN environment variable is not set")
    
    productsBatch = ProductSearchItem()
    for product in req.products:
        productsBatch.add_item(product.item_code, product.title)
        parsed_items = productsBatch.get_items_parssed()

    completer = LLMCompleter(
        api_key=api_key,
        model_name='gpt-4o',
        embedding_model_name='openai/text-embedding-3-small',   
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md',
        base_url=base_url,
    )

    return completer.get_product_enrichment_data(products=parsed_items)


