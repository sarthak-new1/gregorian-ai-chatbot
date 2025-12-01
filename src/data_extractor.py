import re
from langchain_community.document_loaders import PyPDFLoader

class DataExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text(self):
        loader = PyPDFLoader(self.pdf_path)

        # Load and parse the PDF
        docs = loader.load()
        
        # Initialize an empty string to hold the extracted text
        full_text = ""
        
        for page in docs:
            text = page.page_content

            # Normalize Unicode whitespace
            text = text.replace("\u00A0", " ")   # NBSP
            text = text.replace("\u200B", "")    # zero-width
            
            full_text += text + "\n"

        # Remove overly repeated newlines
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)

        return full_text.strip()
