from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from services.matching import match
from services.parser import extract_text_from_pdf
from services.skills import extract_skills
from services.suggestions import generate_suggestions
import shutil
import os

from fastapi import FastAPI, UploadFile, File
from s3_upload import upload_resume

app = FastAPI()


app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    with open(file.filename, "wb") as f:
        f.write(await file.read())

    upload_resume(file.filename, file.filename)

    return {"message": "Resume uploaded to AWS S3"}
# ================= HOME PAGE =================
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ATS Resume Analyzer</title>
        <style>
            body{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg,#0f172a,#1e293b);
                color:white;
                padding:40px;
            }
            .box{
                max-width:800px;
                margin:auto;
                background:#111827;
                padding:30px;
                border-radius:18px;
                box-shadow:0 10px 30px rgba(0,0,0,0.4);
            }
            h1{text-align:center;}
            input,textarea,button{
                width:100%;
                padding:12px;
                margin-top:12px;
                border:none;
                border-radius:10px;
                font-size:16px;
            }
            textarea,input{
                background:#1f2937;
                color:white;
            }
            button{
                background:#22c55e;
                color:black;
                font-weight:bold;
                cursor:pointer;
            }
            button:hover{
                opacity:0.9;
            }
            .result{
                margin-top:20px;
                background:#0b1220;
                padding:15px;
                border-radius:12px;
                white-space:pre-wrap;
            }
            .bar-bg{
                width:100%;
                height:18px;
                background:#374151;
                border-radius:999px;
                margin-top:15px;
            }
            .bar{
                height:100%;
                width:0%;
                border-radius:999px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ATS Resume Analyzer 🚀</h1>
            <p>Upload Resume PDF and Paste Job Description</p>

            <form id="resumeForm">
                <input type="file" name="file" accept=".pdf" required>
                <textarea name="job_description" rows="8" placeholder="Paste Job Description Here..." required></textarea>
                <button type="submit">Analyze Resume</button>
            </form>

            <div class="bar-bg">
                <div class="bar" id="scoreBar"></div>
            </div>

            <div class="result" id="output">Results will appear here...</div>
        </div>

        <script>
            document.getElementById("resumeForm").onsubmit = async function(e){
                e.preventDefault();

                document.getElementById("output").innerText = "Analyzing...";
                let formData = new FormData(this);

                let response = await fetch("/upload-resume", {
                    method: "POST",
                    body: formData
                });

                let data = await response.json();

                if(data.error){
                    document.getElementById("output").innerText = data.error;
                    return;
                }

                let score = Math.round(data.match_score * 100);

                let bar = document.getElementById("scoreBar");
                bar.style.width = score + "%";

                if(score >= 75){
                    bar.style.background = "#22c55e";
                }else if(score >= 50){
                    bar.style.background = "#eab308";
                }else{
                    bar.style.background = "#ef4444";
                }

                document.getElementById("output").innerText =
                    "ATS Score: " + score + "%\\n\\n" +
                    "Matched Skills: " + data.matched_skills.join(", ") + "\\n\\n" +
                    "Missing Skills: " + data.missing_skills.join(", ") + "\\n\\n" +
                    "Suggestions: " + data.suggestions.join(", ");
            }
        </script>
    </body>
    </html>
    """


# ================= API =================
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
    except:
        return {"error": "Invalid PDF File"}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    # 🔥 Improved scoring logic
    base_score = match(resume_text, job_description)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    # Skill score
    if len(job_skills) > 0:
        skill_score = len(matched) / len(job_skills)
    else:
        skill_score = 0

    # Final score
    final_score = (0.6 * base_score) + (0.4 * skill_score)

    suggestions = generate_suggestions(missing)

    return {
        "match_score": final_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions
    }
