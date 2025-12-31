import re
from typing import Dict, List, Optional

class FingerprintAnalyzer:
    """
    AI Writer Fingerprinting (Stylometry)
    Identifies specific AI models based on lexical bias, structural patterns, and metadata.
    """
    
    # Lexical Biases (The 'DNA' of different models)
    AI_SIGNATURES = {
        "GPT-4 / GPT-4o": {
            "keywords": [
                r"\bdelve\b", r"\bcomprehensive\b", r"\btransformative\b", 
                r"\bvibrant\b", r"\btapestry\b", r"\bembark\b", 
                r"\bmeticulous\b", r"\btestament\b", r"\bfoster\b"
            ],
            "threshold": 1
        },
        "Claude (Anthropic)": {
            "keywords": [
                r"I understand that", r"Actually,", r"It's important to note",
                r"however,", r"I apologize if", r"Let's look at this"
            ],
            "threshold": 2
        },
        "Gemini (Google)": {
            "keywords": [
                r"\bHere are\b", r"\blet's explore\b", r"\bkey takeaway\b",
                r"\bin summary\b", r"\bconsider this\b"
            ],
            "threshold": 1
        }
    }

    @staticmethod
    def identify_source(text: str, ai_probability: float) -> Optional[str]:
        """
        Determines the most likely AI source if ai_probability is high.
        """
        if ai_probability < 30.0:
            return None # Not likely AI, don't fingerprint
            
        scores = {}
        text_lower = text.lower()
        
        for model, config in FingerprintAnalyzer.AI_SIGNATURES.items():
            match_count = 0
            for pattern in config["keywords"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    match_count += 1
            
            if match_count >= config["threshold"]:
                scores[model] = match_count
        
        if not scores:
            # Fallback for general AI
            if ai_probability > 80:
                return "Generative AI (Undefined)"
            return None

        # Return the model with the highest signature match
        return max(scores, key=scores.get)
