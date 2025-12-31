import re

class CitationHandler:
    def __init__(self):
        # Patterns for academic citations and direct quotes
        self.patterns = {
            # Direct quotes with double quotes "..." or “...”
            "direct_quote": re.compile(r'["“][^"”]{30,}["”]', re.IGNORECASE),
            
            # APA/MLA style like (Author, 2023) or [1, 2]
            "parenthetical": re.compile(r'\(\b[A-Z][a-z]+,?\s\d{4}\)', re.UNICODE),
            "bracketed": re.compile(r'\[\d{1,3}(,\s?\d{1,3})*\]'),
            
            # Bibliography format like "Name, A. B. (YYYY)" or "Name, A. B., & Other, C."
            "bib_style": re.compile(r'^[A-Z][a-z]+,?\s[A-Z](\.\s?[A-Z]?)*,?\s?(&\s?[A-Z][a-z]+)?.*\(?\d{4}\)?', re.MULTILINE),
            
            # URLs and DOIs
            "url": re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+|doi\.org/[^\s<>"]+', re.IGNORECASE),

            # Citation/Bibliography Headers
            "headers": re.compile(r'\b(DAFTAR PUSTAKA|REFERENCES|BIBLIOGRAPHY|DAFTAR RUJUKAN)\b', re.IGNORECASE),

            # Introductory phrases common in academic citations in Indonesian
            "intro_indonesian": re.compile(
                r'\b(menurut|berdasarkan|seperti yang dinyatakan oleh|selaras dengan|merujuk pada|sesuai pasal|sebagaimana|seperti dikutip dari)\b', 
                re.IGNORECASE
            )
        }

    def is_citation(self, text: str) -> bool:
        """
        Determines if a given sentence or fragment is a citation or direct quote.
        """
        # 0. Check for Headers or URLs (High priority for data exclusion)
        if self.patterns["headers"].search(text) or self.patterns["url"].search(text):
            return True

        # 1. Check for long direct quotes
        if any(self.patterns["direct_quote"].finditer(text)):
            return True
            
        # 2. Check for parenthetical citations or bibliography markers
        if (self.patterns["parenthetical"].search(text) or 
            self.patterns["bracketed"].search(text) or
            self.patterns["bib_style"].search(text)):
            return True
            
        # 3. Check for specific Indonesian intro markers (Heuristic)
        if self.patterns["intro_indonesian"].search(text) and len(text.split()) < 40:
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
