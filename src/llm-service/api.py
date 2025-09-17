from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import YandexGPTService
import logging

app = FastAPI(title='LLM Service')
llm = YandexGPTService()


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str


class TokenResponse(BaseModel):
    iam_token: str


@app.post('/ask', response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        answer = llm.ask_gpt(request.question)
        return QuestionResponse(answer=answer)
    except Exception as e:
        logging.error(f'Error processing question: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/iam-token', response_model=TokenResponse)
async def get_iam_token():
    try:
        token = llm.get_iam_token()
        return TokenResponse(iam_token=token)
    except Exception as e:
        logging.error(f'Error getting IAM token: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))
