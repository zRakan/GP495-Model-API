from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

COLLECTION = "SQL"
CLIENT = QdrantClient(host='localhost', port=6333) 

if(not CLIENT.collection_exists(collection_name=COLLECTION)):
    CLIENT.create_collection(
        collection_name=COLLECTION,
        vectors_config={"fast-bge-small-en": VectorParams(size=384, distance=Distance.COSINE)}
    )

def getRAG(input, collection=COLLECTION, limit=10):
    search_result = CLIENT.query(
        collection_name=collection,
        query_text=input,
        limit=limit
    )
    return search_result