from flask import Blueprint, request, jsonify, session
import sqlite3
import bcrypt
import database

# Inline security functions
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({"error": "All fields required"}), 400
    
    conn = database.get_db_connection()
    try:
        user_id = database.generate_id()
        password_hash = hash_password(password)
        
        conn.execute('''
            INSERT INTO users (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, email, password_hash))
        conn.commit()
        
        return jsonify({"message": "User registered", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = database.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Return user data (in real app, use JWT or session)
    return jsonify({
        "message": "Login successful",
        "user_id": user['user_id'],
        "name": user['name'],
        "email": user['email']
    }), 200

@bp.route('/logout', methods=['POST'])
def logout():
    # In a real app, invalidate session/token
    return jsonify({"message": "Logged out"}), 200