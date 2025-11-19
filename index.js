db.embedded_movies.createSearchIndex(
  "vector_index", 
  "vectorSearch", 
  {
    "fields": [
      {
        "type": "vector",
        "path": "SementicVector",
        "numDimensions": 1536,
        "similarity": "dotProduct",
        "quantization": "scalar"
      }
    ]
  }
);