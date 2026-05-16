"""
matcher.py
──────────
Core skill-extraction + match-scoring engine.
Uses spaCy for NLP and a curated skill lexicon for extraction.
TF-IDF cosine similarity acts as a semantic top-up on top of exact matching.
"""

import re
from typing import Dict, Set, List
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ── Load spaCy model ──────────────────────────────────────────────────────────
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback: blank model (no NER, but lexicon scan still works perfectly)
    nlp = spacy.blank("en")


# ── Master skill lexicon (tech + soft skills) ─────────────────────────────────
SKILL_LEXICON: Set[str] = {
    # Programming languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "rust",
    "kotlin", "swift", "r", "matlab", "scala", "php", "ruby", "bash", "shell",
    "powershell", "dart", "lua", "perl",

    # ML / AI / Data Science
    "machine learning", "deep learning", "neural network", "natural language processing",
    "nlp", "computer vision", "reinforcement learning", "transfer learning",
    "generative ai", "large language model", "llm", "gpt", "bert", "transformer",
    "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch", "xgboost",
    "lightgbm", "catboost", "hugging face", "langchain", "openai", "stable diffusion",
    "diffusion model", "rag", "retrieval augmented generation", "embeddings",
    "fine-tuning", "prompt engineering", "mlops", "feature engineering",
    "model evaluation", "hyperparameter tuning", "cross-validation",
    "classification", "regression", "clustering", "dimensionality reduction",
    "pca", "t-sne", "umap",

    # Data
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "bokeh",
    "data analysis", "data visualization", "data cleaning", "data preprocessing",
    "etl", "data pipeline", "data engineering", "data warehousing",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "cassandra",
    "elasticsearch", "neo4j", "bigquery", "snowflake", "databricks",
    "apache spark", "pyspark", "hadoop", "kafka", "airflow", "dbt",
    "tableau", "power bi", "looker",

    # Web / APIs
    "fastapi", "flask", "django", "rest api", "graphql", "grpc", "websocket",
    "html", "css", "react", "next.js", "vue", "angular", "node.js", "express",
    "streamlit", "gradio",

    # Cloud / DevOps / MLOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins", "linux", "git", "github", "gitlab",
    "mlflow", "wandb", "weights and biases", "dvc", "sagemaker", "vertex ai",
    "lambda", "ec2", "s3",

    # Automation / RPA
    "selenium", "playwright", "puppeteer", "beautiful soup", "scrapy",
    "zapier", "make", "n8n", "rpa", "automation", "web scraping",

    # Soft skills
    "communication", "teamwork", "problem solving", "critical thinking",
    "leadership", "time management", "project management", "agile", "scrum",
    "research", "collaboration", "presentation", "documentation",

    # General
    "api integration", "unit testing", "pytest", "debugging", "version control",
    "object-oriented programming", "oop", "functional programming",
    "microservices", "system design", "algorithm", "data structure",
}

# Build a sorted list for multi-word matching (longest first)
_SORTED_SKILLS = sorted(SKILL_LEXICON, key=len, reverse=True)


def _normalise(text: str) -> str:
    """Lowercase, collapse whitespace, remove punctuation noise."""
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str) -> Set[str]:
    """
    Extract skills from text using two passes:
      1. Lexicon scan (exact multi-word match on normalised text).
      2. spaCy NER pass for any PRODUCT/ORG/etc. entities that overlap with lexicon.
    """
    norm = _normalise(text)
    found: Set[str] = set()

    # Pass 1 – lexicon substring match
    for skill in _SORTED_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, norm):
            found.add(skill)

    # Pass 2 – spaCy entity hints (label: PRODUCT, ORG, GPE often carries tech terms)
    doc = nlp(text[:50000])  # cap to avoid memory issues on huge docs
    for ent in doc.ents:
        ent_norm = _normalise(ent.text)
        if ent_norm in SKILL_LEXICON:
            found.add(ent_norm)

    return found


def tfidf_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between two documents via TF-IDF."""
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf = vec.fit_transform([text_a, text_b])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(np.clip(sim, 0.0, 1.0))
    except Exception:
        return 0.0


def screen_resume(resume_text: str, job_description: str) -> Dict:
    """
    Main entry point.

    Returns
    -------
    dict with keys:
        resume_skills      – skills found in the resume
        jd_skills          – skills found in the JD
        matched_skills     – intersection
        missing_skills     – in JD but not in resume
        match_percentage   – blended score (0-100)
        tfidf_score        – raw cosine sim (0-1)
    """
    resume_skills: Set[str] = extract_skills(resume_text)
    jd_skills: Set[str] = extract_skills(job_description)

    matched: Set[str] = resume_skills & jd_skills
    missing: Set[str] = jd_skills - resume_skills

    # Skill match ratio
    skill_score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0

    # TF-IDF semantic similarity (gives partial credit for paraphrased skills)
    tfidf_sim = tfidf_similarity(resume_text, job_description)
    tfidf_score_pct = tfidf_sim * 100

    # Blended: 70% skill coverage + 30% semantic similarity
    blended = 0.70 * skill_score + 0.30 * tfidf_score_pct
    blended = round(float(np.clip(blended, 0, 100)), 1)

    suggestions = generate_suggestions(missing, matched)

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": blended,
        "tfidf_score": round(tfidf_sim, 4),
        "suggestions": suggestions,
    }


# ── Suggestion categories ─────────────────────────────────────────────────────

_SUGGESTION_MAP = [
    {
        "skills": {"tableau", "power bi", "looker", "data visualization", "matplotlib", "seaborn", "plotly"},
        "icon": "📊",
        "title": "Add Data Visualization Tools",
        "desc_template": "The JD requires {skills}. Add these explicitly to your Skills section.",
        "priority": "high",
    },
    {
        "skills": {"aws", "gcp", "azure", "sagemaker", "vertex ai", "lambda", "ec2", "s3"},
        "icon": "☁️",
        "title": "Mention Cloud Platform Experience",
        "desc_template": "Cloud skills like {skills} are listed as preferred. Add any exposure — even personal projects count.",
        "priority": "medium",
    },
    {
        "skills": {"git", "github", "gitlab"},
        "icon": "🔀",
        "title": "List Version Control Skills",
        "desc_template": "{skills} is expected in most tech roles. Add it to your Skills or Tools section.",
        "priority": "high",
    },
    {
        "skills": {"communication", "presentation", "collaboration", "teamwork"},
        "icon": "🗣️",
        "title": "Highlight Soft Skills Explicitly",
        "desc_template": "The JD specifically mentions {skills}. Add a brief line in your summary or experience.",
        "priority": "medium",
    },
    {
        "skills": {"docker", "kubernetes"},
        "icon": "🐳",
        "title": "Add Containerization Skills",
        "desc_template": "{skills} is mentioned in the JD. Include any project where you used containers.",
        "priority": "medium",
    },
    {
        "skills": {"etl", "apache spark", "airflow", "kafka", "dbt", "data pipeline"},
        "icon": "🔧",
        "title": "Add Data Engineering / Pipeline Skills",
        "desc_template": "The role needs {skills}. Mention any ETL or pipeline work in your projects.",
        "priority": "medium",
    },
    {
        "skills": {"sql", "mysql", "postgresql"},
        "icon": "🗄️",
        "title": "Make SQL Experience Visible",
        "desc_template": "{skills} is required. Quantify your SQL work (e.g. 'queried 1M+ row datasets').",
        "priority": "high",
    },
    {
        "skills": {"web scraping", "selenium", "scrapy", "beautiful soup"},
        "icon": "🕷️",
        "title": "Include Web Scraping Projects",
        "desc_template": "{skills} is listed as a bonus. Add any scraping project to your GitHub.",
        "priority": "low",
    },
    {
        "skills": {"zapier", "make", "n8n", "automation", "rpa"},
        "icon": "⚙️",
        "title": "Showcase Automation Experience",
        "desc_template": "Automation tools like {skills} are a bonus. Mention any workflow automation work.",
        "priority": "low",
    },
    {
        "skills": {"fastapi", "flask", "django", "rest api"},
        "icon": "🚀",
        "title": "Add API / Backend Framework Skills",
        "desc_template": "{skills} is in the JD. Include any API project — even a small Flask/FastAPI app counts.",
        "priority": "medium",
    },
    {
        "skills": {"machine learning", "scikit-learn", "tensorflow", "pytorch", "xgboost"},
        "icon": "🤖",
        "title": "Quantify ML Project Results",
        "desc_template": "You have {skills} — make the impact measurable (accuracy %, dataset size, business outcome).",
        "priority": "high",
    },
    {
        "skills": {"nlp", "natural language processing", "bert", "llm", "hugging face"},
        "icon": "💬",
        "title": "Highlight NLP Experience",
        "desc_template": "{skills} is listed. Detail your NLP work with specific models and datasets used.",
        "priority": "medium",
    },
]


def generate_suggestions(missing: Set[str], matched: Set[str]) -> List[Dict]:
    """
    Generate actionable resume suggestions based on missing skills.
    Returns a prioritised list of suggestion dicts.
    """
    suggestions = []
    seen_categories = set()

    for cat in _SUGGESTION_MAP:
        cat_id = cat["title"]
        if cat_id in seen_categories:
            continue

        # skills from this category that are missing
        missing_in_cat = missing & cat["skills"]
        # skills from this category that are already matched
        matched_in_cat = matched & cat["skills"]

        if not missing_in_cat:
            continue

        skill_str = ", ".join(f"`{s}`" for s in sorted(missing_in_cat))
        desc = cat["desc_template"].format(skills=skill_str)

        # Downgrade priority if candidate already has some skills in the category
        priority = cat["priority"]
        if matched_in_cat and priority == "high":
            priority = "medium"

        suggestions.append({
            "icon":     cat["icon"],
            "title":    cat["title"],
            "desc":     desc,
            "priority": priority,
            "skills":   missing_in_cat,
        })
        seen_categories.add(cat_id)

    # Sort: high → medium → low
    order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: order.get(x["priority"], 3))
    return suggestions[:6]  # cap at 6 suggestions