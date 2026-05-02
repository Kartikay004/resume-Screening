from fastapi import FastAPI, UploadFile, File, Form
from app.services.matching import match
from app.services.parser import extract_text_from_pdf
from app.services.skills import extract_skills
from app.services.suggestions import generate_suggestions
import shutil

app = FastAPI()

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume_text = extract_text_from_pdf(file_path)
    except Exception as e:
        return {"error": "Invalid PDF"}

    score = match(resume_text, job_description)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    suggestions = generate_suggestions(missing)

    # ✅ IMPORTANT RETURN
    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions
    }