from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import tempfile, os
from pdf2image import convert_from_bytes
from io import BytesIO
import re

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "file required"}), 400
    f = request.files['file']
    content = f.read()
    filename = f.filename.lower()

    images = []
    if filename.endswith('.pdf'):
        images = convert_from_bytes(content)
    else:
        img = Image.open(BytesIO(content))
        images = [img]

    full_text = []
    for img in images:
        page_text = pytesseract.image_to_string(img)
        full_text.append(page_text)

    text = "\n\n---PAGE_BREAK---\n\n".join(full_text)

    invoice_no = None
    m = re.search(r"invoice\s*no[:#\-\s]*(\w+)", text, flags=re.I)
    if m:
        invoice_no = m.group(1)
    total = None
    m2 = re.search(r"total\s*[:\-\$\s]*([0-9,.]+)", text, flags=re.I)
    if m2:
        total = m2.group(1)

    return jsonify({"raw_text": text, "invoice_no": invoice_no, "total": total})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)
