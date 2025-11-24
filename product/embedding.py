from typing import List
from product.output import ItemProductDetailsResponse
import openai


class VectorEmbedding:
    def __init__(self, api_key: str, model_name: str, base_url: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.prompt_template = {}
        self.client= openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
    
    def __get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        embeddings = [data.embedding for data in response.data]
        print(f"Embeddings , total {response.usage.total_tokens} tokens used.") 

        return embeddings
    
    def get_embeddings(self, items: ItemProductDetailsResponse) -> ItemProductDetailsResponse:
        texts = [self.__concatenate_and_prepare_for_embedding(item.title,item.short_description, [p.text for p in item.item_description.paragraphs]) for item in items.items]
        response = self.__get_batch_embeddings(texts)
        for item, embedding in zip(items.items, response):
            item.sementic_vector = embedding
        return items
    def get_embedding(self, text: str) -> List[float]:
        prepared_text = self.__perpareTextForEmbedding(text)
        response = self.client.embeddings.create(
            model=self.model_name,
            input=[prepared_text]
        )
        embedding = response.data[0].embedding
        return embedding
        

    def __perpareTextForEmbedding(self,text: str) -> str:
        # Basic preprocessing: lowercasing and stripping whitespace
        preprocessed_text = text.lower().strip()
        return preprocessed_text

    def __concatenate_and_prepare_for_embedding(self,title:str,short_description:str,item_description: List[str], separator: str = " ") -> str:
    
        # Concatenate with separator
        concatenated_item_description = separator.join(item_description) 
        concatenated_item_description = concatenated_item_description.strip()
        concatenated_text = f"{title} {short_description} {concatenated_item_description}".strip()
        # Prepare for embedding (preprocess)
        prepared_text = self.__perpareTextForEmbedding(concatenated_text)

        
        return prepared_text