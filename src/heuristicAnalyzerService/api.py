from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import PreCheckService
import logging

app = FastAPI(title="PreCheck Service")
precheck = PreCheckService()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PreCheckRequest(BaseModel):
    text: str


class PreCheckResponse(BaseModel):
    malicious: bool
    pattern: str | None = None


@app.post("/precheck", response_model=PreCheckResponse)
async def precheck_text(request: PreCheckRequest):
    try:
        is_malicious = precheck.is_malicious(request.text)
        pattern = precheck.get_detected_pattern(request.text) if is_malicious else None
        return PreCheckResponse(malicious=is_malicious, pattern=pattern)
    except Exception as e:
        logger.error(f'Ошибка при precheck: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))
