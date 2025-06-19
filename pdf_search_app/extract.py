from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pdf_search_app.models import Contract
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
import openai


def generate_summary(text):
    if not text.strip():
        return ""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize this contract for internal reference."},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return response['choices'][0]['message']['content'].strip()

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
                ocr_text = image_to_string(images[0], lang='spa') 
                text += ocr_text
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_artist_name(text):
    match = re.search(r'LA COMPAÑÍA\);\s+y\s+(.+?)\s+\(denominado EL ARTISTA\)', text)
    if match:
        return match.group(1).strip()
    return 'Unknown'

def extract_date(text):
    # ex looks for "CONTRATO hecho este "
    start = text.find("CONTRATO hecho este ")
    if start != -1:
        date_end = text.find(",", start)
        return text[start + len("CONTRATO hecho este "):date_end].strip()
    return "Unknown"

def extract_keywords(text):
    # ex return first 3 unique significant words
    words = list(set(text.lower().split()))
    return ', '.join(words[:3]) if words else "None"

def normalize_whitespace(text):
    return ' '.join(text.split())

def extract_metadata(filepath):
    if filepath.lower().endswith(".pdf"):
        text = extract_text_from_pdf(filepath)
        text = normalize_whitespace(text)
    elif filepath.lower().endswith(".docx"):
        text = extract_text_from_docx(filepath)
    else:
        print(f"Unsupported file type: {filepath}")
        return {}

    return {
        "artist_name": extract_artist_name(text),
        "date": extract_date(text),
        "keywords": extract_keywords(text),
        "affiliation": "",  
        "content": text
    }


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
            text = normalize_whitespace(text)  
        elif filename.lower().endswith('.docx'):
            text = extract_text_from_docx(filepath)
        else:
            print(f"Unsupported file type: {filename}")
            continue

        print(f"\n--- {filename} ---")
        print(text[:500])  # preview first 500 characters


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

print("\n=== SUMMARY OF CONTRACTS EXTRACTED ===")
for c in contracts:
    print(f"{c['filename']} | Artist: {c['artist_name']} | Date: {c['date']} | Keywords: {c['keywords']}")


for contract in contracts:
    existing = session.query(Contract).filter_by(filename=contract['filename']).first()
    if existing:
        continue  

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

def process_folder(folder_path):
    import os
    from pdf_search_app.models import Contract
    from pdf_search_app import db
    from pdf_search_app.extract import extract_metadata

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith((".pdf", ".docx")):
                file_path = os.path.join(root, filename)

                relative_path = os.path.relpath(file_path, start=folder_path)

                print(f"📄 Processing: {file_path}")
                data = extract_metadata(file_path)

                # Prevent duplicates by checking full relative path
                existing = Contract.query.filter_by(filename=relative_path).first()
                if existing:
                    continue

                contract = Contract(
                    filename=relative_path, 
                    artist_name=data.get("artist_name", ""),
                    date=data.get("date", ""),
                    keywords=data.get("keywords", ""),
                    affiliation=data.get("affiliation", ""),
                    preview=data.get("content", "")[:300]
                )
                db.session.add(contract)

    db.session.commit()
    print("All mock contracts processed and added.")



