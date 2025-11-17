
from typing import List
import openai
from product.output import ItemProductDetailsResponse

class ProductSerchItem:
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
    def __init__(self,base_url: str, api_key: str ,model_name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.prompt_template = {}
        self.client= openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
    
    def load_prompt_template(self,template_name: str,template_file_path: str) -> str:
        prompt= open(template_file_path).read()
        self.prompt_template[template_name]=prompt
       
    def erich_text(self,template_name: str,text: str) -> str:
        if template_name not in self.prompt_template:
            raise ValueError(f"Prompt template '{template_name}' not loaded.")
        
        prompt = self.prompt_template[template_name]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
          
        )
        
        json_content = response.choices[0].message.content
        try:
            product_response = ItemProductDetailsResponse.model_validate_json(json_content)
            return product_response
        except Exception as e:
            print(f"Validation error: {e}")
            print(f"Response: {json_content}")
            raise
        

    

    

