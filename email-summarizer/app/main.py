from fastapi import FastAPI
from pydantic import BaseModel
import re
from sklearn.feature_extraction.text import TfidfVectorizer

app = FastAPI(title="Email Summarizer")

class EmailIn(BaseModel):
    subject: str = ""
    body: str
    max_sentences: int = 3

@app.post('/summarize')
async def summarize(email: EmailIn):
    text = (email.subject + "\n" + email.body).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= email.max_sentences:
        return {"summary": " ".join(sentences)}

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        X = vectorizer.fit_transform(sentences)
    except Exception:
        return {"summary": " ".join(sentences[:email.max_sentences])}

    scores = X.sum(axis=1).A1
    ranked_ix = scores.argsort()[::-1][:email.max_sentences]
    ranked_ix = sorted(ranked_ix)
    summary = " ".join([sentences[i] for i in ranked_ix])
    return {"summary": summary}

@app.get('/health')
async def health():
    return {"status": "ok"}
