🧭 API Documentation
1️⃣ Overview
Service	Description	Example Port	Base URL
resume-parser	Extracts structured information from resumes (skills, experience, education)	8000	http://localhost:8000
invoice-ocr	Extracts and analyzes invoice details using OCR	8002	http://localhost:8002
email-summarizer	Summarizes email content using an LLM model	8001	http://localhost:8001
gateway	Central routing layer that aggregates and forwards requests to all AI services	8080	http://localhost:8080

All services expose a /health endpoint for readiness checks.

2️⃣ Resume Parser Service
Base URL
http://localhost:8000

Endpoints
POST /parse

Extract structured information from a resume file.

Request

curl -X POST http://localhost:8000/parse \
  -F "file=@resume.pdf"


Response

{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "skills": ["Python", "FastAPI", "AWS"],
  "experience_years": 5
}

POST /enqueue-parse

Queue resume parsing as a background task (Celery).

Request

curl -X POST http://localhost:8000/enqueue-parse \
  -F "file=@resume.pdf"


Response

{
  "task_id": "a7f2bdfc-71b2-48d7-a45e-11111b2caa92"
}

GET /health
{"status": "ok"}

3️⃣ Invoice OCR Service
Base URL
http://localhost:8002

Endpoints
POST /extract

Extract invoice text using OCR.

Request

curl -X POST http://localhost:8002/extract \
  -F "file=@invoice.png"


Response

{
  "vendor": "ACME Corp",
  "invoice_number": "INV-102",
  "total_amount": 1200.75,
  "date": "2025-03-15"
}

POST /enqueue-invoice

Process invoice asynchronously.

Request

curl -X POST http://localhost:8002/enqueue-invoice \
  -F "file=@invoice.png"


Response

{"task_id": "fb88990c-9d2c-4f9a-b31b-ff0923f27c0a"}

GET /health
{"status": "ok"}

4️⃣ Email Summarizer Service
Base URL
http://localhost:8001

Endpoints
POST /summarize

Summarize an email (either text or uploaded file).

Request (Form-based)

curl -X POST http://localhost:8001/summarize \
  -F "text=This is a long business email that needs summarization."


Request (File upload)

curl -X POST http://localhost:8001/summarize \
  -F "file=@email.txt"


Response

{
  "summary": "The email provides a concise update about quarterly sales performance."
}

POST /enqueue-summarize

Queue the summarization process in the background (Celery).

Request

curl -X POST http://localhost:8001/enqueue-summarize \
  -F "text=This is a long email for background processing."


Response

{"task_id": "7bcd9e8f-1234-4fd3-8acb-11b8c3a4422e"}

GET /health
{"status": "ok"}

5️⃣ API Gateway Service
Base URL
http://localhost:8080


The gateway forwards client requests to specific microservices using internal routing.

Route	Description	Forwarded To
/resume/parse	Parse resumes	Resume Parser Service
/invoice/extract	Extract invoice data	Invoice OCR Service
/email/summarize	Summarize emails	Email Summarizer Service
Example Request
curl -X POST http://localhost:8080/email/summarize \
  -F "text=This is a detailed project update email."


Response

{"summary": "A brief overview of the project update email."}

6️⃣ Health and Monitoring

Each service exposes:

GET /health


✅ Returns 200 OK when the service is healthy.

For Prometheus/Grafana setup (optional):

Metrics endpoint: /metrics (if integrated)

Grafana dashboards visualize response time, task queue length, etc.

7️⃣ Authentication (optional for production)

You can secure APIs using:

JWT-based auth with FastAPI’s OAuth2PasswordBearer

API Keys passed in headers

Example:

Authorization: Bearer <token>

8️⃣ Error Responses
Code	Meaning	Example
400 Bad Request	Invalid input or missing file	{"error": "No text provided"}
404 Not Found	Route not found	{"detail": "Not Found"}
500 Internal Server Error	Unexpected error in model or Celery	{"error": "Internal server error"}
9️⃣ Integration with Java Backend

The Java backend can:

Make REST calls to these endpoints

Poll task results from Redis or Celery backend

Aggregate and display results via APIs or dashboards

Example (Java → Python):

POST http://localhost:8080/email/summarize
Content-Type: application/json
{
  "text": "Quarterly financial report is ready for review."
}


Response:

{
  "summary": "Quarterly report is available for review."
}

🔚 Summary Table
Service	Key Endpoint	Description
Resume Parser	/parse	Parse candidate resumes
Invoice OCR	/extract	Extract text & fields from invoices
Email Summarizer	/summarize	Summarize emails or text
Gateway	/email/summarize	Unified routing for all services
Celery	enqueue-*	Background task queue for async processing
