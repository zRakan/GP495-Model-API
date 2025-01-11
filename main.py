from fastapi import FastAPI, HTTPException

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
    
class messageRewrite(BaseModel):
    previous: str
    current: str

@app.post('/rewriteMessage')
async def rewriteMessage(message: messageRewrite):
    try:
        return Agent.rewriteQuestion(message.previous, message.current)
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
        dataPoints = RAG.getAllDataPoints()
        return {"data": dataPoints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))