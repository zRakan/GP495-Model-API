from functools import wraps

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointIdsList

COLLECTION = "SQL"

CLIENT = False
try:
    initClient = QdrantClient(host='localhost', port=6333)
    initClient.http.ping()

    CLIENT = initClient
except Exception as e:
    pass

# Decorator
def require_qdrant(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not CLIENT:
            return [] 
        
        return func(*args, **kwargs)
    return wrapper


if(CLIENT and not CLIENT.collection_exists(collection_name=COLLECTION)):
    CLIENT.create_collection(
        collection_name=COLLECTION,
        vectors_config={"fast-bge-small-en": VectorParams(size=384, distance=Distance.COSINE)}
    )

@require_qdrant
def getRAG(input, collection=COLLECTION, limit=10, score=0):
    search_result = CLIENT.query(
        collection_name=collection,
        query_text=input,
        limit=limit
    )

    filtered_result = [
        response
        for response in search_result if response.score >= score
    ]

    return filtered_result

@require_qdrant
def getAllDataPoints(collection=COLLECTION):
    dataPoints = []

    nextCursor = None
    scrolling = True

    while scrolling:
        documents, nextCursor = CLIENT.scroll(
            collection_name=collection,
            limit=500,
            offset=nextCursor,
            with_payload=True,
            with_vectors=False
        )

        scrolling = nextCursor is not None

        dataPoints.extend(documents)
    
    return dataPoints

@require_qdrant
def addData(document, answer):
    return CLIENT.add(
        collection_name=COLLECTION,
        documents=[document],
        metadata=[{ "query": answer }]
    )

@require_qdrant
def editData(id, document, answer):
    return CLIENT.overwrite_payload(
        collection_name=COLLECTION,
        payload={
            "document": document,
            "query": answer
        },
        points=PointIdsList(points=[id])        
    )

@require_qdrant
def removeData(id):
    return CLIENT.delete(
        collection_name=COLLECTION,
        points_selector=PointIdsList(points=[id])
    )