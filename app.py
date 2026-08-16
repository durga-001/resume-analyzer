import os
import json

from dotenv import load_dotenv
load_dotenv()  

from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import Base, engine, SessionLocal
import models
import PyPDF2
import docx

from ai import analyze_resume  # <-- this import was missing/commented out before, breaking every analysis

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# Create database tables if they don't exist yet
Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        db = SessionLocal()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            db.close()
            return render_template("signup.html", error="Email and password are required.")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            db.close()
            return render_template("signup.html", error="User already exists.")

        user = models.User(email=email, password_hash=generate_password_hash(password))
        db.add(user)
        db.commit()
        db.close()
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = SessionLocal()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.query(models.User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user"] = user.email
            db.close()
            return redirect("/dashboard")

        db.close()
        return render_template("login.html", error="Invalid credentials.")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role", "").strip()
        resume_text = request.form.get("resume", "").strip()
        file = request.files.get("file")

        # File handling (PDF / DOCX upload overrides pasted text)
        if file and file.filename != "":
            if file.filename.lower().endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}
            elif file.filename.lower().endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = "\n".join(p.text for p in doc.paragraphs)
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Docx error: {str(e)}"}
            else:
                result = {"error": "Unsupported file type. Please upload a .pdf or .docx file."}

        if result is None:
            if not resume_text or not user_goal:
                result = {"error": "Please provide both a resume and a target role."}
            else:
                try:
                    result = analyze_resume(resume_text, user_goal)

                    db = SessionLocal()
                    user = db.query(models.User).filter_by(email=session["user"]).first()
                    report = models.Reports(
                        user_id=user.id,
                        resume_text=resume_text,
                        target_role=user_goal,
                        ats_score=result.get("ats_score", 0),
                        result=json.dumps(result),
                    )
                    db.add(report)
                    db.commit()
                    db.close()
                except Exception as e:
                    result = {"error": f"AI error: {str(e)}"}

    return render_template("dashboard.html", user=session["user"], result=result)


@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()
    reports = db.query(models.Reports).filter_by(user_id=user.id).order_by(models.Reports.id.desc()).all()

    parsed_reports = []
    for r in reports:
        try:
            parsed_result = json.loads(r.result)
        except Exception:
            parsed_result = {}
        parsed_reports.append({
            "resume": r.resume_text,
            "target_role": r.target_role,
            "ats_score": r.ats_score,
            "result": parsed_result,
        })
    db.close()

    return render_template("history.html", reports=parsed_reports)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")