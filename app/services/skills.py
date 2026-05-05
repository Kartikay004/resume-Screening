SKILL_MAP = {
    "python": ["python"],
    "java": ["java"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "javascript": ["javascript", "js"],
    "react": ["react", "reactjs"],
    "nodejs": ["nodejs", "node"],
    "sql": ["sql"],
    "mongodb": ["mongodb", "mongo"],
    "aws": ["aws", "amazon web services"],
    "docker": ["docker"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "html": ["html"],
    "css": ["css"],
}

def extract_skills(text):
    text = text.lower()
    found = []

    for skill, keywords in SKILL_MAP.items():
        for keyword in keywords:
            if keyword in text:
                found.append(skill)
                break

    return list(set(found))
