import json
import re
import spacy  # Temporarily disabled
nlp=None

# Skill dictionary (can be expanded)
SKILL_PATTERNS = {
    'Programming': ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby'],
    'Web': ['HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask'],
    'Cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'CI/CD'],
    'Data': ['SQL', 'Pandas', 'NumPy', 'Tableau', 'Power BI', 'Excel', 'R'],
    'AI/ML': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'scikit-learn'],
    'Soft Skills': ['Team Leadership', 'Communication', 'Agile', 'Scrum', 'Project Management']
}

def get_nlp_model():
    def get_nlp_model():
     """Load spaCy model (cached)"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load('en_core_web_sm')
        except OSError:
            # model not present → download once
            print("Downloading spaCy model …")
            spacy.cli.download('en_core_web_sm')
            nlp = spacy.load('en_core_web_sm')
    return nlp
def extract_skills(text: str, nlp) -> list:
    """Extract skills from text using rule-based matching"""
    skills_found = []
    text_lower = text.lower()
    
    # Convert skill patterns to lowercase for matching
    for category, skill_list in SKILL_PATTERNS.items():
        for skill in skill_list:
            if skill.lower() in text_lower:
                # Check for word boundaries to avoid partial matches
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    skills_found.append(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = [x for x in skills_found if not (x in seen or seen.add(x))]
    
    return unique_skills

def extract_education(text: str, nlp) -> list:
    """Extract education information"""
    doc = nlp(text)
    education = []
    
    # Look for education patterns
    education_keywords = ['bachelor', 'master', 'phd', 'bs', 'ba', 'ms', 'mba']
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            education.append(line.strip())
    
    return education[:3]  # Limit to top 3 entries

def extract_experience(text: str, nlp) -> list:
    """Extract work experience"""
    doc = nlp(text)
    experience = []
    
    # Look for year patterns and company names
    experience_patterns = [
        r'(\d+)\s*years?\s+of\s+experience',
        r'(\d+)-(\d+)\s*years?',
        r'(present|current|today)',
    ]
    
    lines = text.split('\n')
    for line in lines:
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in experience_patterns):
            experience.append(line.strip())
    
    return experience[:5]  # Limit to top 5 entries