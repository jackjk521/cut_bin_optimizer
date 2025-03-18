# FastAPI Contract Filler

This is a FastAPI-based application that:
1. Accepts a CSV file containing data.
2. Accepts a DOCX file as a contract template with placeholders.
3. Fills the placeholders based on CSV data.
4. Converts the filled DOCX files to PDFs.
5. Automatically downloads the filled PDF.

## 📦 Requirements
- Python 3.8+
- Install dependencies:
  ```bash
  pip install fastapi uvicorn python-docx docx2pdf pandas
