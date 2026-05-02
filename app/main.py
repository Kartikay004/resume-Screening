from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from services.matching import match
from services.parser import extract_text_from_pdf
from services.skills import extract_skills
from services.suggestions import generate_suggestions
import shutil, os

app = FastAPI()

@app.get('/', response_class=HTMLResponse)
def home():
    return '''<!DOCTYPE html><html><head><title>ATS Resume Analyzer</title><style>body{font-family:Arial;background:linear-gradient(135deg,#0f172a,#1e293b);padding:40px;color:#fff}.box{max-width:760px;margin:auto;background:#111827;padding:28px;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.35)}h1{margin-top:0}input,textarea,button{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:none}textarea,input{background:#1f2937;color:#fff}button{background:#22c55e;color:#08110a;font-weight:700;cursor:pointer}.meter{height:16px;background:#374151;border-radius:999px;overflow:hidden;margin:12px 0}.bar{height:100%;width:0%}.card{background:#0b1220;padding:14px;border-radius:12px;margin-top:12px;white-space:pre-wrap}</style></head><body><div class="box"><h1>ATS Resume Analyzer</h1><p>Upload your resume and paste job description.</p><form id="f"><input type="file" name="file" accept=".pdf" required><textarea name="job_description" rows="8" placeholder="Paste job description" required></textarea><button type="submit">Analyze Resume</button></form><div class="meter"><div class="bar" id="bar"></div></div><div class="card" id="out">Results will appear here...</div></div><script>document.getElementById('f').onsubmit=async(e)=>{e.preventDefault();document.getElementById('out').textContent='Analyzing...';const fd=new FormData(e.target);const r=await fetch('/upload-resume',{method:'POST',body:fd});const j=await r.json();if(j.error){document.getElementById('out').textContent=j.error;return;}const score=Math.round(j.match_score||0);const bar=document.getElementById('bar');bar.style.width=score+'%';bar.style.background=score>75?'#22c55e':score>50?'#eab308':'#ef4444';document.getElementById('out').textContent='ATS Score: '+score+'%\n\nMatched Skills: '+j.matched_skills.join(', ')+'\n\nMissing Skills: '+j.missing_skills.join(', ')+'\n\nSuggestions: '+j.suggestions.join(', ');}</script></body></html>'''

@app.post('/upload-resume')
async def upload_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        resume_text = extract_text_from_pdf(file_path)
    except Exception:
        return {'error':'Invalid PDF'}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    score = match(resume_text, job_description)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    suggestions = generate_suggestions(missing)
    return {'match_score':score,'matched_skills':matched,'missing_skills':missing,'suggestions':suggestions}
