db.productEnrichedDb.createSearchIndex(
  "vector_index", 
  "vectorSearch", 
  {
    "fields": [
      {
        "type": "vector",
        "path": "SementicVector",
        "numDimensions": 1536,
        "similarity": "cosine",
        "quantization": "scalar"
      }
    ]
  }
);

db.productEnrichedDb.aggregate(
   [
      {
         $listSearchIndexes:
            {
           
            }
      }
   ]
);
db.runCommand({
  dropSearchIndex: "vector_index",
  collection: "productEnrichedDb"
});