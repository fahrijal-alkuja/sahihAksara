import re

class CitationHandler:
    def __init__(self):
        # Patterns for academic citations and direct quotes
        self.patterns = {
            # Direct quotes with double quotes "..." or “...”
            "direct_quote": re.compile(r'["“][^"”]{30,}["”]', re.IGNORECASE),
            
            # APA/MLA style like (Author, 2023) or [1, 2]
            # Now expanded to support (Name, Year: Page) or (Name, Year, hal. 10)
            "body_note": re.compile(r'\(\b[A-Z][a-z]+,?\s\d{4}([:\s,]+(hal\.|p\.)?\s?\d+[-–]?\d*)?\)', re.UNICODE),
            "bracketed": re.compile(r'\[\d{1,3}(,\s?\d{1,3})*\]'),
            
            # Footnote content format (e.g., "1 Nama Penulis, Judul...")
            "footnote_content": re.compile(r'^\d{1,3}\s+[A-Z][a-z]+.*,.*(19|20)\d{2}.*', re.MULTILINE),
            
            # Traditional footnote markers
            "footnote_markers": re.compile(r'\b(Ibid\.|Op\.cit\.|Loc\.cit\.)\b', re.IGNORECASE),

            # Indonesian Legal Citations (e.g., Pasal 27 ayat (1) UUD 1945)
            "legal_citation": re.compile(r'\b(Pasal|Ayat|Undang-Undang|UU|UUD|Peraturan|Permen|Kepmen)\b\s+\d+.*', re.IGNORECASE),

            # Bibliography format like "Name, A. B. (YYYY)" or "Name, A. B., & Other, C."
            "bib_style": re.compile(r'^[A-Z][a-z]+,?\s[A-Z](\.\s?[A-Z]?)*,?\s?(&\s?[A-Z][a-z]+)?.*\(?\d{4}\)?', re.MULTILINE),
            
            # URLs and DOIs
            "url": re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+|doi\.org/[^\s<>"]+', re.CASE_INSENSITIVE),

            # Citation/Bibliography Headers
            "headers": re.compile(r'\b(DAFTAR PUSTAKA|REFERENCES|BIBLIOGRAPHY|DAFTAR RUJUKAN|CATATAN KAKI|FOOTNOTES)\b', re.IGNORECASE),

            # Introductory phrases common in academic citations in Indonesian
            "intro_indonesian": re.compile(
                r'\b(menurut|berdasarkan|seperti yang dinyatakan oleh|selaras dengan|merujuk pada|sesuai pasal|sebagaimana|seperti dikutip dari|dikemukakan oleh|pernyataan dari)\b', 
                re.IGNORECASE
            )
        }

    def is_citation(self, text: str) -> bool:
        """
        Determines if a given sentence or fragment is a citation or direct quote.
        """
        # 0. Check for Headers, URLS, or Legal Citations (High priority data exclusion)
        if (self.patterns["headers"].search(text) or 
            self.patterns["url"].search(text) or 
            self.patterns["legal_citation"].search(text)):
            return True

        # 1. Check for long direct quotes
        if any(self.patterns["direct_quote"].finditer(text)):
            return True
            
        # 2. Check for reference markers & body notes
        if (self.patterns["body_note"].search(text) or 
            self.patterns["bracketed"].search(text) or
            self.patterns["bib_style"].search(text) or
            self.patterns["footnote_content"].search(text) or
            self.patterns["footnote_markers"].search(text)):
            return True
            
        # 3. Check for specific Indonesian intro markers (Heuristic)
        if self.patterns["intro_indonesian"].search(text) and len(text.split()) < 45:
            return True

        return False

    def mask_citations(self, sentences: list) -> list:
        """
        Processes a list of sentence dictionaries and marks them.
        """
        processed = []
        for s in sentences:
            text = s.get("text", "")
            if self.is_citation(text):
                s["is_citation"] = True
            else:
                s["is_citation"] = False
            processed.append(s)
        return processed
