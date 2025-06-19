## JNOrganizer

**Internal Contract Management Web Application**
Built for JN Music, Secure, Local Network Only

### Project Overview
**JNOrganizer** is a secure, internal-use web application developed for **JN Music** to help digitalize, organize, and search throughout its extensive catalog of artist-related contracts and business agreements. The platform supports metadata extraction, full-text search, and user-based activity tracking, with a focus on privacy, ease of access, and long-term scalability.

### Purpose
This application addresses the current challenge of managing a large number of documents (PDF, DOCX, scanned files) stored on a local company disk. The system allows employees to:
- Search documents through various filters
- View AI-generated contract summaries (This feature still being implemented as have to review security risks)
- Edit metadata fields
- Upload new contracts with automated metadata extraction ( via PyPDF2 + OCR fallback )
- Track uploads, edits, and views via a user-specific activity log
- Maintain **strict data privacy** - all documents are stored and accessed locally only

### Tech Stack
- **Language**: Python 3.12
- **Web Framework**: Flask
- **Database**: SQLite (  via SQLAlchemy ORM )
- **Document Parsing**: PyPDF2 + Tesseract OCR
- **UI Templates**: Jinja2/HTML/CSS
- **Virtual Environment**: Python 'venv'
- **Version Control**: Git + Github
- **User Authentication**: Flask-Login + Flask-WTF

### Security Model
- **Local-only access**: The app runs on the company's internal machine and is served to other employees only via the **local network (LAN)**.
- **No internet hosting**: No documents or data are sent or stored externally.
- **User login system**: Access requires username/email + password.
- **Activity logging**: Tracks document uploads, edits, and views per user.
- **Environment isolation**: All dependencies are contained in a virtual environment using `venv`.
- **Sensitive paths configured via `.env` file** — never hardcoded.

### Key Features

### Document Metadata Extraction
- Uses `PyPDF2` to parse text from digital PDFs or Docx
- Falls back to `pytesseract` (OCR) via `pdf2image` for scanned contracts
- Extracts: `artist name`, `date`, `keywords`, `affiliation`

### Search & Filter
- Users can search contracts using:
  - Full-text keyword match
  - Artist name or affiliation
  - Date filters (exact or ranges)
  - File name
- Upcoming: SQLite FTS5 or Whoosh for full-text indexing

### File Upload
- Secure uploads with `secure_filename`
- Metadata auto-filled after upload
- Stored only on local shared drive defined by `.env`

### Contract Editing
- Authenticated users can edit metadata (except file name)
- Edits are logged with user info and timestamp

### User System & Activity Log
- Each user has a profile with tracked document activity
- View and edit logs available to admin or user dashboard

## Deployment Plan
- **Local deployment only** — the Flask app runs on the shared company computer.
- Accessed internally using IP-based URL
