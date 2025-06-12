from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Contract, Base
from pdf2image import convert_from_path
from pytesseract import image_to_string
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
from PIL import Image
import os
from pypdf import PdfReader
import docx
import re
import csv


def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    text = ''
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text and page_text.strip():
            text += page_text
        else:
            # Fallback to OCR if page has no extractable text
            images = convert_from_path(filepath, first_page=page_num + 1, last_page=page_num + 1)
            if images:
                ocr_text = image_to_string(images[0], lang='spa')  # Assuming Spanish contracts
                text += ocr_text
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_artist_name(text):
    # This will find the name just before "(denominado EL ARTISTA)"
    match = re.search(r'LA COMPAÑÍA\);\s+y\s+(.+?)\s+\(denominado EL ARTISTA\)', text)
    if match:
        return match.group(1).strip()
    return 'Unknown'

def extract_date(text):
    # Dummy example: looks for "CONTRATO hecho este "
    start = text.find("CONTRATO hecho este ")
    if start != -1:
        date_end = text.find(",", start)
        return text[start + len("CONTRATO hecho este "):date_end].strip()
    return "Unknown"

def extract_keywords(text):
    # Dummy example: return first 3 unique significant words
    words = list(set(text.lower().split()))
    return ', '.join(words[:3]) if words else "None"

def normalize_whitespace(text):
    return ' '.join(text.split())

CONTRACT_DIR = "/Users/victoriav/Documents/JNOrganizer/MockContracts"

engine = create_engine('sqlite:///contracts.db')
Session = sessionmaker(bind=engine)
session = Session()

contracts = []

for root, dirs, files in os.walk(CONTRACT_DIR):
    for filename in files:
        filepath = os.path.join(root, filename)

        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
            text = normalize_whitespace(text)  # 👈 normalize PDF spacing
        elif filename.lower().endswith('.docx'):
            text = extract_text_from_docx(filepath)
        else:
            print(f"Unsupported file type: {filename}")
            continue

        print(f"\n--- {filename} ---")
        print(text[:500])  # preview first 500 characters


    # text = extracted from file
        artist_name = extract_artist_name(text)
        contract_date = extract_date(text)
        keywords = extract_keywords(text)
    
        contracts.append({
            'filename': filename,
            'artist_name': artist_name,
            'date': contract_date,
            'keywords': keywords,
            'preview': text[:500],
        })

# Optional: print all collected metadata
print("\n=== SUMMARY OF CONTRACTS EXTRACTED ===")
for c in contracts:
    print(f"{c['filename']} | Artist: {c['artist_name']} | Date: {c['date']} | Keywords: {c['keywords']}")


for contract in contracts:
    existing = session.query(Contract).filter_by(filename=contract['filename']).first()
    if existing:
        continue  # Skip duplicates

    new_entry = Contract(
        filename=contract['filename'],
        artist_name=contract['artist_name'],
        date=contract['date'],
        keywords=contract['keywords'],
        preview=contract['preview'],
    )
    session.add(new_entry)

session.commit()
print("Contracts successfully added to the database!")