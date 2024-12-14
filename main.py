from fastapi import FastAPI, HTTPException
from utils import database

app = FastAPI()

@app.get('/')
@app.get('/generate-questions')
async def generate_questions():
    try:
        schema = database.extract_schema()
        questions = database.generate_questions(schema)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))