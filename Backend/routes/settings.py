# backend/routes/settings.py
from flask import Blueprint, request, jsonify
import database
import os
import shutil

bp = Blueprint('settings', __name__)


@bp.route('/clear-data', methods=['POST'])
def clear_data():
    """
    Deletes everything for one user:
    – DB rows (users, resumes, analyses – cascade handles children)
    – uploaded PDF files
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    conn = database.get_db_connection()

    # 1.  collect file paths before we delete rows
    resumes = conn.execute(
        'SELECT file_path FROM resumes WHERE user_id = ?', (user_id,)
    ).fetchall()

    # 2.  delete user (ON DELETE CASCADE removes resumes & analyses automatically)
    conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    # 3.  remove physical PDFs
    for r in resumes:
        try:
            os.remove(r['file_path'])
        except FileNotFoundError:
            pass  # already gone

    return jsonify({"message": "All data cleared"}), 200