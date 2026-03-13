from pypdf import PdfReader
import io

def extract_text_from_pdf(file_stream):
    """Extract text from a PDF file stream."""
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return None

def extract_text_from_file(file):
    """General file text extraction based on extension."""
    filename = file.filename.lower()
    file_stream = io.BytesIO(file.read())
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_stream)
    elif filename.endswith('.txt'):
        return file_stream.getvalue().decode('utf-8', errors='ignore')
    else:
        # Fallback to direct decode for other text-based files
        return file_stream.getvalue().decode('utf-8', errors='ignore')
