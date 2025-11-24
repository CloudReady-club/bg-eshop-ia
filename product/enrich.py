from typing import List
import openai
from  product.output import parse_item_product_details_response
from product.embedding import VectorEmbedding
from mongodb.item import ItemProductDetails
from mongodb.mongod import utc_now
from product.embedding import VectorEmbedding

class ProductSearchItem:
    def __init__(self):
        self.item_list= []

    def add_item(self,product_id: str, product_title:str ):
        self.item_list.extend([{product_id:product_title}]) 
    def get_items(self):
        return self.item_list
    def get_items_parssed(self):
        parsed_items = []
        for item in self.item_list:
            for product_id, product_title in item.items():
                parsed_items.append(f'{product_id}:{product_title}')
        return ' | '.join(parsed_items)
    def clear_items(self):
        self.item_list.clear()
    
    
   
class LLMCompleter:
    def __init__(self, api_key: str ,model_name: str,
                    embedding_model_name: str,
                    template_name: str,template_file_path: str,
                    base_url: str= None):
        
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.embedding = VectorEmbedding(
                api_key=self.api_key,
                model_name=embedding_model_name,
                base_url=self.base_url
            )
        
        self.prompt_template = {}
        self.client= openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        self.__load_prompt_template(template_name,template_file_path)
    
    def __load_prompt_template(self,template_name: str,template_file_path: str) -> str:
        prompt= open(template_file_path).read()
        self.prompt_template[template_name]=prompt
       
    def __erich_text(self,template_name: str,text: str) -> str:
        if template_name not in self.prompt_template:
            raise ValueError(f"Prompt template '{template_name}' not loaded.")
        
        prompt = self.prompt_template[template_name]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
          
        )
        json_content = response.choices[0].message.content
        product_items= parse_item_product_details_response(json_content)
        product_items = self.embedding.get_embeddings(product_items) 
        print(f"Enrichement:{response.usage.prompt_tokens} prompt tokens used, {response.usage.completion_tokens} completion tokens used, total {response.usage.total_tokens} tokens used.") 
        return product_items
    
    def process_products_enrichment(self, products:list[ItemProductDetails] = None, product:ItemProductDetails=None ) -> list[ItemProductDetails]:
        if not products and not product:
           raise ValueError("Either 'products' list or 'product' must be provided.")
        if product and not products:
            products = [product]   
            return self.__process_products_enrichment(products)
        if  products and len(products) > 0:
            return self.__process_products_enrichment(products)
        else:
            raise ValueError("The 'products' list is empty.")
    def get_product_enrichment_data(self, products:str) :
        if not products:
           raise ValueError("The 'product' must be provided.")
        return self.__erich_text('batch_product_prompt', products)
        
    def __process_products_enrichment(self, products:list[ItemProductDetails] = []) -> list[ItemProductDetails]:
        productsBatch = ProductSearchItem()
        for product in products:
            productsBatch.add_item(product.item_code, product.title)
            parsed_items = productsBatch.get_items_parssed()
        print(f"Processing batch with items: {parsed_items}")
        enriched_text = self.__erich_text(template_name='batch_product_prompt', text=parsed_items)
       
        for product,item in zip(products,enriched_text.items):
            product.sementic_vector = item.sementic_vector
            product.short_description = item.short_description
            product.item_description = item.item_description
            product.item_specification = item.item_specification
            product.search_status = item.search_status
            product.sources = item.sources
            product.tags = item.tags
            product.last_modification = utc_now()

        return products

        

    

    

