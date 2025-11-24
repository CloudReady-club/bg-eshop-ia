# app.py

import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from fastapi import FastAPI, HTTPException
from product.enrich import LLMCompleter
app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.get("/product-information/{product}")
def search(product: str):
    base_url='https://models.github.ai/inference'
    api_key = os.environ.get("GITHUB_TOKEN")
    if not api_key:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN environment variable is not set")

    completer = LLMCompleter(
        api_key=api_key,
        model_name='gpt-4o',
        embedding_model_name='openai/text-embedding-3-small',
        template_name='batch_product_prompt',
        template_file_path='batch_product_prompt.md',
        base_url=base_url,
    )

    return completer.get_product_enrichment_data(products=product)


