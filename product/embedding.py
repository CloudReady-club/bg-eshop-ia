from typing import List
from product.output import ItemProductDetailsResponse
import openai


class VectorEmbedding:
    def __init__(self, base_url, api_key: str, model_name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.prompt_template = {}
        self.client= openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        embedding = response.data[0].embedding
        return embedding
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        embeddings = [data.embedding for data in response.data]
        return embeddings
    
    def get_embeddings(self, items: ItemProductDetailsResponse) -> ItemProductDetailsResponse:
        texts = [concatenate_and_prepare_for_embedding([item.title,item.short_description]) for item in items.items]
        response = self.get_batch_embeddings(texts)
        for item, embedding in zip(items.items, response):
            item.sementic_vector = embedding
        return items
        

def perpareTextForEmbedding(text: str) -> str:
    # Basic preprocessing: lowercasing and stripping whitespace
    preprocessed_text = text.lower().strip()
    return preprocessed_text

def concatenate_and_prepare_for_embedding(texts: List[str], separator: str = " | ") -> str:
    # Filter out empty strings and None values
    filtered_texts = [text for text in texts if text and isinstance(text, str)]
    # Concatenate with separator
    concatenated_text = separator.join(filtered_texts)
    # Prepare for embedding (preprocess)
    prepared_text = perpareTextForEmbedding(concatenated_text)
    
    return prepared_text