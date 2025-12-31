import fitz  # PyMuPDF
from docx import Document
import io

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF with smart cleanup."""
        text = ""
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            pages = []
            for page in doc:
                # 1. Extract raw text
                raw = page.get_text()
                # 2. Smart Cleanup: Replace single newlines with spaces (joining sentences)
                # but keep double newlines (paragraph boundaries)
                clean = raw.replace("\n\n", "[[PARA]]").replace("\n", " ").replace("[[PARA]]", "\n\n")
                pages.append(clean)
            doc.close()
            text = "\n\n".join(pages)
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
        return text

    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        text = []
        try:
            doc = Document(io.BytesIO(file_content))
            for para in doc.paragraphs:
                text.append(para.text)
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
        return "\n".join(text)

    def process_file(self, filename: str, content: bytes) -> str:
        """Route file to appropriate extractor based on extension."""
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            return self.extract_text_from_pdf(content)
        elif ext == "docx":
            return self.extract_text_from_docx(content)
        elif ext == "txt":
            return content.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file format: {ext}")
