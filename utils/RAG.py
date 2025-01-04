from qdrant_client import QdrantClient

CLIENT = QdrantClient(host='localhost', port=6333) 

def getRAG(input, collection="SQL", limit=10):
    search_result = CLIENT.query(
        collection_name=collection,
        query_text=input,
        limit=limit
    )
    return search_result