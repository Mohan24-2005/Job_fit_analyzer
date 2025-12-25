from flask import Blueprint, request, jsonify
import json
import pdfplumber
import database
from models.nlp_processor import extract_skills, extract_education, extract_experience, get_nlp_model
from models.embeddings import generate_embedding
import os

# Inline PDF parser
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text.strip()

bp = Blueprint('resume', __name__)

@bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files allowed"}), 400
    
    # Save file
    filename = f"{user_id}_{file.filename}"
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    # Extract text
    text = extract_text_from_pdf(filepath)
    if not text:
        os.remove(filepath)
        return jsonify({"error": "Could not extract text from PDF"}), 400
    
    # Process with NLP
    nlp = get_nlp_model()
    skills = extract_skills(text, nlp)
    education = extract_education(text, nlp)
    experience = extract_experience(text, nlp)
    
    # Generate embedding
    embedding_blob = generate_embedding(text)
    
    # Store in database
    conn = database.get_db_connection()
    resume_id = database.generate_id()
    
    conn.execute('''
        INSERT INTO resumes (resume_id, user_id, file_name, file_path, parsed_text, 
                           skills, education, experience, resume_embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id, user_id, filename, filepath, text,
        json.dumps(skills), json.dumps(education), json.dumps(experience),
        embedding_blob
    ))
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Resume uploaded and processed",
        "resume_id": resume_id,
        "skills": skills,
        "skill_count": len(skills)
    }), 201