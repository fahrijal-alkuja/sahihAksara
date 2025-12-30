from core.ai_detector import AIDetector
import sys
import os

# Add backend to path to import core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_granular_language_guard():
    detector = AIDetector()
    
    text = (
        "Ini adalah naskah akademik yang ditulis dalam Bahasa Indonesia. "
        "Namun, di dalamnya terdapat kutipan dalam Bahasa Inggris: \"The world is a stage, and all the men and women merely players.\" "
        "Semoga sistem tetap mendeteksinya sebagai Bahasa Indonesia dan mengabaikan kutipan bahasa Inggris tersebut."
    )
    
    print(f"Testing text: {text}\n")
    result = detector.analyze(text)
    
    print(f"Probability: {result['ai_probability']}%")
    print(f"Status: {result['status']}")
    print("\nSentences Analysis:")
    for sent in result['sentences']:
        label = "ID" if sent['score'] != -1 else "EN (Ignored)"
        print(f"[{label}] Score: {sent['score']} | Text: {sent['text']}")

if __name__ == "__main__":
    test_granular_language_guard()
