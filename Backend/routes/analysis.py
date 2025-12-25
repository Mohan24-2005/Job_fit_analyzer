# backend/routes/analysis.py
from flask import Blueprint, request, jsonify
import database
from models.embeddings import get_embedding_from_bytes, model as embed_model
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from models.nlp_processor import extract_skills   # reuse rule-based extractor
import json

# ------------------------------------------------------------------
#  Rich learning-path repository (offline, localhost-safe)
# ------------------------------------------------------------------
LEARNING_PATH = {
    "Docker": {
        "videos": ["https://www.youtube.com/watch?v=zJ6WbK9zFpI",
                   "https://www.youtube.com/watch?v=PgTzP9pkaQA"],
        "hours": 6,
        "project": "Build a multi-container Node+Postgres app",
        "certificate": "Docker Certified Associate"
    },
    "Kubernetes": {
        "videos": ["https://www.youtube.com/watch?v=X48VuDVv0do",
                   "https://www.youtube.com/watch?v=s_o8dwzR6p4"],
        "hours": 10,
        "project": "Deploy micro-services on minikube with auto-scaling",
        "certificate": "CKAD"
    },
    "AWS": {
        "videos": ["https://www.youtube.com/watch?v=3hLmDS179YE",
                   "https://www.youtube.com/watch?v=Z027y5mxaHY"],
        "hours": 15,
        "project": "Host a static site + CI/CD pipeline",
        "certificate": "AWS Cloud Practitioner"
    },
    "Python": {
        "videos": ["https://www.youtube.com/watch?v=rfscVS0vtbw",
                   "https://www.youtube.com/watch?v=7lmCu8wz8ro"],
        "hours": 20,
        "project": "Automate a daily report with pandas + e-mail",
        "certificate": "PCAP – Certified Associate"
    },
    "Machine Learning": {
        "videos": ["https://www.youtube.com/watch?v=7eh4d6sAB6A",
                   "https://www.youtube.com/watch?v=NWONeJYa6rM"],
        "hours": 25,
        "project": "End-to-end churn prediction API with Flask",
        "certificate": "TensorFlow Developer Cert"
    },
    "SQL": {
        "videos": ["https://www.youtube.com/watch?v=HXV3zeQKqGY",
                   "https://www.youtube.com/watch?v=9S8z8S0hw8w"],
        "hours": 8,
        "project": "Design & query a Netflix-style DB",
        "certificate": "Oracle SQL Certified"
    },
    "React": {
        "videos": ["https://www.youtube.com/watch?v=bMknfKXIFA8",
                   "https://www.youtube.com/watch?v=TiSGujMifOI"],
        "hours": 12,
        "project": "Todo-app + unit tests + CI deploy",
        "certificate": "React Developer Cert"
    },
    "Node.js": {
        "videos": ["https://www.youtube.com/watch?v=TlB_eWDSMt4",
                   "https://www.youtube.com/watch?v=Oe421EPjeBE"],
        "hours": 10,
        "project": "REST API with auth + Swagger docs",
        "certificate": "OpenJS Node.js Services Cert"
    },
    "Figma": {
        "videos": ["https://www.youtube.com/watch?v=FTFaQWZBqQ8"],
        "hours": 4,
        "project": "Design a 5-screen mobile app",
        "certificate": "Figma Skill Certificate"
    },
    "Git": {
        "videos": ["https://www.youtube.com/watch?v=SWYqp7iY_Tc"],
        "hours": 3,
        "project": "Contribute to an open-source repo",
        "certificate": "GitHub Foundations"
    },
    "JavaScript": {
        "videos": ["https://www.youtube.com/watch?v=W6NZfCO5SIk"],
        "hours": 8,
        "project": "Build a weather dashboard with fetch API",
        "certificate": "JavaScript Algorithms & Data Structures"
    },
    "CSS": {
        "videos": ["https://www.youtube.com/watch?v=yfoY53QXElI"],
        "hours": 4,
        "project": "Clone a landing page pixel-perfect",
        "certificate": "CSS Specialist"
    },
    "HTML": {
        "videos": ["https://www.youtube.com/watch?v=pQN-pnXPaVg"],
        "hours": 2,
        "project": "Build accessible semantic pages",
        "certificate": "HTML5 Specialist"
    }
    # Add more skills here – if not listed, the fallback below will auto-create a card
}


# ------------------------------------------------------------------
#  Rich roadmap generator
# ------------------------------------------------------------------
def generate_recommendations(missing_skills: list, match_score: float) -> dict:
    """
    Returns a learning path object:
      short_term  -> list of {skill, videos[], hours, project, certificate}
      medium_term -> list of strings
      long_term   -> list of strings
    """
    short_term = []
    for skill in missing_skills[:3]:                       # top 3 gaps
        if skill in LEARNING_PATH:
            short_term.append({
                "skill": skill,
                "videos": LEARNING_PATH[skill]["videos"],
                "hours": LEARNING_PATH[skill]["hours"],
                "project": LEARNING_PATH[skill]["project"],
                "certificate": LEARNING_PATH[skill]["certificate"]
            })

    # fallback if no mapped skill
    if not short_term:
        short_term.append({
            "skill": "Resume",
            "videos": ["https://www.youtube.com/watch?v=JyRFzoGpdMs"],
            "hours": 2,
            "project": "Quantify achievements with metrics",
            "certificate": "LinkedIn Learning Resume Course"
        })

    # strategic horizons
    if match_score < 60:
        medium = ["Build 2 portfolio projects", "Contribute to open-source", "Obtain one certificate above"]
        long   = ["Target mid-level roles", "Build 5+ significant projects"]
    elif match_score < 80:
        medium = ["Deepen 2 core tech stacks", "Lead a small team/task", "Pass one certificate"]
        long   = ["Aim for senior roles", "Speak at meet-ups / write blogs"]
    else:
        medium = ["Prepare for system-design interviews", "Mentor juniors"]
        long   = ["Target staff / principal level", "Develop domain expertise"]

    return {
        "short_term": short_term,
        "medium_term": medium,
        "long_term": long
    }


bp = Blueprint('analysis', __name__)


@bp.route('/job-roles', methods=['GET'])
def get_job_roles():
    conn = database.get_db_connection()
    roles = conn.execute('SELECT role_id, role_name, industry FROM job_roles').fetchall()
    conn.close()
    return jsonify({
        "roles": [{"role_id": r['role_id'], "role_name": r['role_name'], "industry": r['industry']}
                  for r in roles]
    }), 200


@bp.route('/analyze-role', methods=['POST'])
def analyze_role():
    data = request.get_json()
    user_id   = data.get('user_id')
    resume_id = data.get('resume_id')
    role_id   = data.get('role_id')

    if not all([user_id, resume_id, role_id]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = database.get_db_connection()

    # ---- fetch resume & role ----
    resume = conn.execute(
        'SELECT resume_embedding, skills FROM resumes WHERE resume_id = ?', (resume_id,)
    ).fetchone()

    job_role = conn.execute(
        'SELECT role_name, job_description, required_skills, jd_embedding '
        'FROM job_roles WHERE role_id = ?', (role_id,)
    ).fetchone()

    if not resume or not job_role:
        conn.close()
        return jsonify({"error": "Resume or job role not found"}), 404

    # ---- embeddings ----
    resume_embedding = get_embedding_from_bytes(resume['resume_embedding'])

    if job_role['jd_embedding'] is None:
        from models.embeddings import generate_embedding
        jd_blob = generate_embedding(job_role['job_description'])
        conn.execute('UPDATE job_roles SET jd_embedding = ? WHERE role_id = ?', (jd_blob, role_id))
        conn.commit()
        job_embedding = get_embedding_from_bytes(jd_blob)
    else:
        job_embedding = get_embedding_from_bytes(job_role['jd_embedding'])

    # ---- similarity score  (NumPy → Python float) ----
    score = float(cosine_similarity(
        resume_embedding.reshape(1, -1),
        job_embedding.reshape(1, -1)
    )[0][0]) * 100

    # ---- skill gap ----
    candidate_skills = set(json.loads(resume['skills']))
    required_skills  = set(json.loads(job_role['required_skills']))
    missing_skills   = list(required_skills - candidate_skills)

    # ---- rich roadmap ----
    recommendations = generate_recommendations(missing_skills, score)

    # ---- persist ----
    analysis_id = database.generate_id()
    conn.execute('''
        INSERT INTO analysis_history (analysis_id, user_id, resume_id, role_id,
                                    job_match_score, missing_skills, recommendations)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, user_id, resume_id, role_id,
        round(score, 1), json.dumps(missing_skills), json.dumps(recommendations)
    ))
    conn.commit()
    conn.close()

    # ---- response ----
    return jsonify({
        "analysis_id": analysis_id,
        "job_match_score": round(score, 1),
        "role_name": job_role['role_name'],
        "matched_skills": list(candidate_skills & required_skills),
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }), 200


@bp.route('/analysis/latest', methods=['GET'])
def get_latest_analysis():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    conn = database.get_db_connection()
    latest = conn.execute('''
        SELECT ah.*, jr.role_name
        FROM analysis_history ah
        JOIN job_roles jr ON ah.role_id = jr.role_id
        WHERE ah.user_id = ?
        ORDER BY ah.timestamp DESC
        LIMIT 1
    ''', (user_id,)).fetchone()
    conn.close()

    if not latest:
        return jsonify({"error": "No analysis found"}), 404

    return jsonify({
        "analysis_id": latest['analysis_id'],
        "job_match_score": latest['job_match_score'],
        "role_name": latest['role_name'],
        "missing_skills": json.loads(latest['missing_skills']),
        "recommendations": json.loads(latest['recommendations']),
        "timestamp": latest['timestamp']
    }), 200


# ------------------------------------------------------------------
#  NEW: analyse free-text job description (no DB row needed)
# ------------------------------------------------------------------
from models.embeddings import generate_embedding, model as embed_model
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@bp.route('/analyze-text', methods=['POST'])
def analyze_text():
    """
    Expects: { user_id, resume_id, job_description: "free text..." }
    Returns: same JSON shape as /analyze-role but without DB storage
    """
    data = request.get_json()
    user_id   = data.get('user_id')
    resume_id = data.get('resume_id')
    job_text  = data.get('job_description', '').strip()

    if not all([user_id, resume_id, job_text]):
        return jsonify({"error": "Missing fields"}), 400

    conn = database.get_db_connection()
    resume = conn.execute(
        'SELECT resume_embedding, skills FROM resumes WHERE resume_id = ?', (resume_id,)
    ).fetchone()
    conn.close()

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # ---- same math as before ----
    resume_embedding = get_embedding_from_bytes(resume['resume_embedding'])
    job_embedding    = embed_model.encode(job_text, convert_to_tensor=True).cpu().numpy()

    score = float(cosine_similarity(
        resume_embedding.reshape(1, -1),
        job_embedding.reshape(1, -1)
    )[0][0]) * 100

    # ---- skill gap vs free text ----
    candidate_skills = set(json.loads(resume['skills']))
    required_skills  = set(extract_skills(job_text, None))   # rule-based, no spaCy needed
    missing_skills   = list(required_skills - candidate_skills)

    # ---- recommendations ----
    recommendations = generate_recommendations(missing_skills, score)

    return jsonify({
        "analysis_id": None,
        "job_match_score": round(score, 1),
        "role_name": "User-defined role",
        "matched_skills": list(candidate_skills & required_skills),
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }), 200