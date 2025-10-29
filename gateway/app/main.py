from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", 8000))
RESUME_URL = os.getenv("RESUME_URL", "http://resume-service:8001")
INVOICE_URL = os.getenv("INVOICE_URL", "http://invoice-ocr:8002")
EMAIL_URL = os.getenv("EMAIL_URL", "http://email-summarizer:8003")

app = FastAPI(title="AI Gateway", description="Gateway for AI Microservices")


@app.get("/health")
async def health():
    return {"status": "gateway ok"}


@app.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """Forward resume file to Resume Parser"""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            r = await client.post(f"{RESUME_URL}/parse-resume", files=files)
            return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoice/ocr")
async def ocr_invoice(file: UploadFile = File(...)):
    """Forward invoice image/pdf to Invoice OCR"""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            r = await client.post(f"{INVOICE_URL}/ocr", files=files)
            return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email/summarize")
async def summarize_email(request: Request):
    """Forward email body to Email Summarizer"""
    try:
        body = await request.json()
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{EMAIL_URL}/summarize", json=body)
            return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
