from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os, re
from typing import List
from pdfminer.high_level import extract_text as pdf_extract_text
import docx

app = FastAPI(title="Resume Parser Service")

SKILLS = [
    "python","java","javascript","react","node","docker","kubernetes","aws","sql","nosql",
    "nlp","machine learning","tensorflow","pytorch","fastapi","flask"
]

def extract_text_from_docx_bytes(b: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
        f.write(b)
        tmp = f.name
    try:
        doc = docx.Document(tmp)
        return "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.remove(tmp)

def extract_text_from_pdf_bytes(b: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(b)
        tmp = f.name
    try:
        return pdf_extract_text(tmp)
    finally:
        os.remove(tmp)

def normalize_text(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower())

def skills_from_text(text: str) -> List[str]:
    t = normalize_text(text)
    return [s for s in SKILLS if s.lower() in t]

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    data = await file.read()
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf_bytes(data)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx_bytes(data)
    elif filename.endswith(".txt"):
        text = data.decode(errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .pdf, .docx, .txt")

    skills = skills_from_text(text)
    score = len(skills)
    analysis = {
        "filename": file.filename,
        "skills_found": skills,
        "skill_score": score,
        "summary": (text[:1000] + "...") if len(text) > 1000 else text
    }
    return JSONResponse(content=analysis)

@app.get("/health")
async def health():
    return {"status": "ok"}
