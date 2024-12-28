from pymongo import MongoClient
from uuid import uuid4


Client = MongoClient('mongodb://localhost:27017/')
Database = Client['Mostaelim']

# Collection related
Collection = Database['Chats']
Collection.create_index('author')
Collection.create_index('id')

def getMessages(chatId):
    chat = Collection.find_one({ 'chatId': chatId })
    if(chat is None):
        raise None
    
    return chat['history']

def addMessage(chatId, messages):
    try:
        # history = getMessages(chatId)

        # # Append message(s)
        # history[:] = [*history, *messages]

        Collection.update_one({ 'chatId': chatId }, { 'history': messages })
    except Exception as e:
        raise Exception(e)