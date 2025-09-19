from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextAnalyzerService import ModerationService
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Moderation API")
moderation = ModerationService()


class ModerateRequest(BaseModel):
    text: str


class ModerateResponse(BaseModel):
    malicious: bool


@app.post("/moderate", response_model=ModerateResponse)
def moderate(request: ModerateRequest):
    try:
        is_malicious = moderation.is_malicious_prompt(request.text)
        return ModerateResponse(malicious=is_malicious)
    except Exception as e:
        logging.error(f'Error getting IAM token: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))
