# backend/database.py
import sqlite3
import os
import json
from datetime import datetime
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'job_fit_analyzer.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()

    # ----------  tables  ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            parsed_text TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            resume_embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS job_roles (
            role_id TEXT PRIMARY KEY,
            role_name TEXT UNIQUE NOT NULL,
            job_description TEXT NOT NULL,
            required_skills TEXT,
            jd_embedding BLOB,
            industry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            analysis_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            resume_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            job_match_score REAL NOT NULL,
            missing_skills TEXT,
            recommendations TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES job_roles(role_id) ON DELETE CASCADE
        )
    ''')

    # ----------  indexes  ----------
    conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id)')

    # ----------  16-role seed  ----------
    cursor = conn.execute('SELECT COUNT(*) as count FROM job_roles')
    if cursor.fetchone()['count'] == 0:
        default_roles = [
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Software Developer',
                'job_description': 'Design, code, test and maintain software applications across the full SDLC.',
                'required_skills': json.dumps(['Python', 'JavaScript', 'Git', 'SQL', 'Algorithms']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Data Analyst',
                'job_description': 'Collect, clean and interpret data to drive business decisions.',
                'required_skills': json.dumps(['SQL', 'Excel', 'Pandas', 'Tableau', 'Statistics']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Machine Learning Engineer',
                'job_description': 'Build, train and deploy ML models at scale.',
                'required_skills': json.dumps(['Python', 'Machine Learning', 'TensorFlow', 'Scikit-learn', 'Docker']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Cloud Engineer',
                'job_description': 'Design, implement and manage cloud infrastructure and services.',
                'required_skills': json.dumps(['AWS', 'Azure', 'Terraform', 'Docker', 'Networking']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'DevOps Engineer',
                'job_description': 'Automate CI/CD, infrastructure and monitoring pipelines.',
                'required_skills': json.dumps(['Docker', 'Kubernetes', 'Jenkins', 'Ansible', 'Python']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'UI/UX Designer',
                'job_description': 'Create user-centred interfaces, wireframes and prototypes.',
                'required_skills': json.dumps(['Figma', 'User Research', 'Prototyping', 'HTML', 'CSS']),
                'industry': 'Design'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Backend Developer',
                'job_description': 'Build server-side logic, APIs and data layers.',
                'required_skills': json.dumps(['Python', 'Node.js', 'REST', 'SQL', 'Git']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Frontend Developer',
                'job_description': 'Implement responsive user interfaces and client-side logic.',
                'required_skills': json.dumps(['JavaScript', 'React', 'CSS', 'HTML', 'Webpack']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Full-Stack Developer',
                'job_description': 'Work on both front-end and back-end codebases.',
                'required_skills': json.dumps(['JavaScript', 'React', 'Node.js', 'SQL', 'Git']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Business Analyst',
                'job_description': 'Bridge business needs and technical solutions via data and process analysis.',
                'required_skills': json.dumps(['Excel', 'SQL', 'Documentation', 'Agile', 'Communication']),
                'industry': 'Business'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Project Manager',
                'job_description': 'Plan, execute and deliver projects on time and within budget.',
                'required_skills': json.dumps(['Agile', 'Scrum', 'Communication', 'Risk Management', 'Leadership']),
                'industry': 'Management'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'System Administrator',
                'job_description': 'Maintain servers, OS, backups and user accounts.',
                'required_skills': json.dumps(['Linux', 'Bash', 'Networking', 'AWS', 'Scripting']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'QA Tester',
                'job_description': 'Design and execute test plans, automate regression suites.',
                'required_skills': json.dumps(['Selenium', 'Manual Testing', 'Python', 'JUnit', 'CI/CD']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Network Engineer',
                'job_description': 'Design, implement and troubleshoot network infrastructure.',
                'required_skills': json.dumps(['Cisco', 'Routing', 'Switching', 'TCP/IP', 'Firewalls']),
                'industry': 'Tech'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Cybersecurity Analyst',
                'job_description': 'Monitor threats, perform vulnerability assessments, implement security controls.',
                'required_skills': json.dumps(['SIEM', 'Penetration Testing', 'Risk Assessment', 'Python', 'Network Security']),
                'industry': 'Security'
            },
            {
                'role_id': str(uuid.uuid4()),
                'role_name': 'Database Administrator',
                'job_description': 'Install, configure, secure and optimise database systems.',
                'required_skills': json.dumps(['SQL', 'PostgreSQL', 'Backup & Recovery', 'Performance Tuning', 'Linux']),
                'industry': 'Tech'
            }
        ]

        for role in default_roles:
            conn.execute('''
                INSERT INTO job_roles (role_id, role_name, job_description, required_skills, industry)
                VALUES (?, ?, ?, ?, ?)
            ''', (role['role_id'], role['role_name'], role['job_description'],
                  role['required_skills'], role['industry']))

    conn.commit()
    conn.close()

def generate_id():
    return str(uuid.uuid4())