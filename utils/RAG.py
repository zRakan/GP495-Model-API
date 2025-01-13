from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointIdsList

COLLECTION = "SQL"
CLIENT = QdrantClient(host='localhost', port=6333) 

if(not CLIENT.collection_exists(collection_name=COLLECTION)):
    CLIENT.create_collection(
        collection_name=COLLECTION,
        vectors_config={"fast-bge-small-en": VectorParams(size=384, distance=Distance.COSINE)}
    )

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

def addData(document, answer):
    return CLIENT.add(
        collection_name=COLLECTION,
        documents=[document],
        metadata=[{ "query": answer }]
    )

def editData(id, document, answer):
    return CLIENT.overwrite_payload(
        collection_name=COLLECTION,
        payload={
            "document": document,
            "query": answer
        },
        points=PointIdsList(points=[id])        
    )

def removeData(id):
    return CLIENT.delete(
        collection_name=COLLECTION,
        points_selector=PointIdsList(points=[id])
    )