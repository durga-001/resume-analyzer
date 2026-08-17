# Career Copilot — AI Resume Analyzer

🔗 **Live demo:** [careercopilot.com](https://resume-analyzer-h9q3.onrender.com/login)

Career Copilot is a Flask web app that analyzes resumes against target job roles using OpenAI’s LLMs. It provides:

- ATS‑style match score  
- Relevant skills detected  
- Missing skills/keywords  
- Personalized learning roadmap  
- Likely interview questions  

---

## 🚀 Features
- Secure signup/login (hashed passwords)  
- Resume input via paste or PDF/DOCX upload  
- AI‑powered analysis with OpenAI API  
- ATS score, skills gap, roadmap, interview prep  
- Persistent history of past analyses  

---

## 🛠 Tech Stack
- **Backend:** Flask, SQLAlchemy  
- **Database:** PostgreSQL (prod) / SQLite (local)  
- **AI:** OpenAI API (`gpt-4.1-mini`)  
- **Parsing:** PyPDF2, python-docx  
- **Deployment:** Render  

