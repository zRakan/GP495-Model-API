from pymongo import MongoClient
from uuid import uuid4


Client = MongoClient('mongodb://localhost:27017/')
Database = Client['Mostaelim']

# Collection related
Collection = Database['Chats']
Collection.create_index('author')
Collection.create_index('id')

def createChannel(authorId, title):
    try:
        channelId = uuid4()
        
        Collection.insert_one({
            "id": channelId,
            "author": authorId,
            "title": title,
            "history": []
        })

        return channelId
    except Exception as e:
        raise Exception(e)


def getMessages(chatId, withDiagrams=False):
    chat = Collection.find_one({ 'chatId': chatId })
    if(chat is None):
        raise None
    
    # Filter out diagrams
    if(not withDiagrams):
        chat['history'] = [ message for message in chat['history'] if "type" not in message ]
    
    return chat['history']

def addMessage(chatId, messages):
    try:
        # history = getMessages(chatId)

        # # Append message(s)
        # history[:] = [*history, *messages]

        Collection.update_one({ 'chatId': chatId }, { 'history': messages })
    except Exception as e:
        raise Exception(e)