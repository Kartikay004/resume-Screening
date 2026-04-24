SKILLS = [
    "python", "java", "c++", "machine learning",
    "deep learning", "nlp", "fastapi", "django",
    "flask", "sql", "mongodb", "docker", "aws",
    "html", "css", "javascript", "react",
    "nodejs", "api", "backend", "frontend"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))