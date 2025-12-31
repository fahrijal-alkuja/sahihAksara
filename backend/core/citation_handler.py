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
            
            # Introductory phrases common in academic citations in Indonesian
            "intro_indonesian": re.compile(
                r'\b(menurut|berdasarkan|seperti yang dinyatakan oleh|selaras dengan|merujuk pada|sesuai pasal)\b', 
                re.IGNORECASE
            )
        }

    def is_citation(self, text: str) -> bool:
        """
        Determines if a given sentence or fragment is a citation or direct quote.
        """
        # 1. Check for long direct quotes (usually high-risk for AI false positive if they are extracts)
        if any(self.patterns["direct_quote"].finditer(text)):
            return True
            
        # 2. Check for parenthetical citations at the end or middle
        if self.patterns["parenthetical"].search(text) or self.patterns["bracketed"].search(text):
            # Only count as citation if it's accompanied by some content, 
            # or if it's just the reference marker itself
            return True
            
        # 3. Check for specific Indonesian intro markers (Heuristic)
        # We only flag it if the sentence is relatively short or clearly a statement from someone else
        if self.patterns["intro_indonesian"].search(text) and len(text.split()) < 35:
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
