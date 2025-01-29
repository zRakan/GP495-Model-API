from fastapi import FastAPI, HTTPException

# Load dotenv
from dotenv import load_dotenv
load_dotenv()

# Redis
import redis
import jsonpickle
client = redis.Redis('localhost', port=6379)

from utils import database
from utils import Agent
from utils import RAG

app = FastAPI()


from pydantic import BaseModel
class messageSend(BaseModel):
    history: list
    message: str

@app.post('/sendMessage')
async def sendMessage(message: messageSend):
    try:
        return Agent.sendPrompt(conversation=message.history, prompt=message.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class sqlRewrite(BaseModel):
    input: str
    invalidSQL: str

@app.post('/fixSQL')
async def fixSQL(message: sqlRewrite):
    try:
        schema = database.extractSchema()
        return Agent.sqlSafeExecute(message.input, message.invalidSQL, schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/suggestions')
async def generate_questions():
    try:
        schema = database.extractSchema()
        questions = Agent.generateQuestions(schema)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/dataList')
async def getDataList():
    try:
        if(client.exists('Mostaelim:RAG:list')):
            dataPoints = jsonpickle.decode(client.get('Mostaelim:RAG:list'))
        else:
            dataPoints = RAG.getAllDataPoints()
            client.set('Mostaelim:RAG:list', jsonpickle.encode(dataPoints)) # Cache it

        return {"data": dataPoints}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


class dataParams(BaseModel):
    question: str
    answer: str

@app.post('/addData')
async def addData(data : dataParams):
    try:
        client.delete('Mostaelim:RAG:list') # Remove from cache
        id = RAG.addData(data.question, data.answer)
        return { "id": id }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class dataParams(BaseModel):
    id: str

@app.post('/removeData')
async def removeData(data : dataParams):
    try:
        client.delete('Mostaelim:RAG:list') # Remove from cache
        status = RAG.removeData(data.id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class dataParams(BaseModel):
    id: str
    query: str
    answer: str

@app.post('/editData')
async def editData(data : dataParams):
    try:
        client.delete('Mostaelim:RAG:list') # Remove from cache
        status = RAG.editData(data.id, data.query, data.answer)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))