# ⚡ RecruitIQ — Resume Screener AI

An AI-powered resume screening tool built with **Streamlit**, **spaCy**, and **TF-IDF**.
Upload a resume (PDF or DOCX), paste a job description, and get an instant match score with actionable improvement suggestions.

---

## Features

- 📄 Upload resumes as **PDF** or **DOCX**
- 🔍 **Skill extraction** via spaCy NLP + curated 100+ skill lexicon
- 📊 **Match scoring** — blended 70% skill coverage + 30% TF-IDF semantic similarity
- ✅ Displays matched skills and missing/gap skills
- 💡 **Improvement suggestions** — tells candidates exactly what to add to boost their score
- 🎨 Professional SaaS-style UI built with Streamlit
- 🔒 100% local — no OpenAI API key needed

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/resume-screener-ai.git
cd resume-screener-ai
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
```

### 3. Install dependencies
```bash
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the app
```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## How It Works