from pypdf import PdfReader
import io
import docx

def extract_text_from_pdf(file_stream):
    """Extract text from a PDF file stream."""
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        import flask
        flask.current_app.logger.error(f"PDF Extraction Error: {e}")
        return None

def extract_text_from_docx(file_stream):
    """Extract text from a DOCX file stream."""
    try:
        doc = docx.Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        import flask
        flask.current_app.logger.error(f"DOCX Extraction Error: {e}")
        return None

def extract_text_from_file(file):
    """General file text extraction based on extension."""
    filename = file.filename.lower()
    file_stream = io.BytesIO(file.read())
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_stream)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file_stream)
    elif filename.endswith('.txt'):
        return file_stream.getvalue().decode('utf-8', errors='ignore')
    else:
        # Fallback to direct decode for other text-based files
        return file_stream.getvalue().decode('utf-8', errors='ignore')
