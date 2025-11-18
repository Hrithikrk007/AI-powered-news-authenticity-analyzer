# file_utils.py
from pathlib import Path
import PyPDF2
import docx

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf","txt","docx"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file_storage):
    filename = file_storage.filename
    safe = "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")).strip()
    dest = UPLOAD_FOLDER / safe
    file_storage.save(dest)
    return str(dest)

def extract_text_from_txt(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def extract_text_from_docx(path):
    try:
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs)
    except Exception:
        return ""

def extract_text_from_pdf(path):
    try:
        reader = PyPDF2.PdfReader(path)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""

def extract_text(path: str):
    ext = path.split(".")[-1].lower()
    if ext == "txt":
        return extract_text_from_txt(path), ext
    if ext == "docx":
        return extract_text_from_docx(path), ext
    if ext == "pdf":
        return extract_text_from_pdf(path), ext
    return "", ext
