import json

def generate_recommendations(missing_skills: list, match_score: float) -> dict:
    """Generate career roadmap based on gaps and score"""
    recommendations = {
        "short_term": [],
        "medium_term": [],
        "long_term": []
    }
    
    # Skill-to-resource mapping
    skill_resources = {
        "Docker": "Complete Docker for Beginners course on Docker Hub",
        "Kubernetes": "Follow Kubernetes official tutorials and minikube setup",
        "AWS": "Get AWS Certified Cloud Practitioner certification",
        "Python": "Practice Python on LeetCode and HackerRank",
        "SQL": "Work through SQLZoo exercises and Mode Analytics tutorials",
        "Machine Learning": "Take Andrew Ng's ML course on Coursera"
    }
    
    # Generate short-term goals (next 1-3 months)
    critical_skills = missing_skills[:3]  # Top 3 most critical
    for skill in critical_skills:
        if skill in skill_resources:
            recommendations["short_term"].append(skill_resources[skill])
    
    if not recommendations["short_term"]:
        recommendations["short_term"].append("Review and update your resume with quantified achievements")
    
    # Medium-term goals (3-6 months)
    if match_score < 60:
        recommendations["medium_term"].append("Focus on building 2-3 projects demonstrating key skills")
        recommendations["medium_term"].append("Contribute to open-source projects to gain experience")
    elif match_score < 80:
        recommendations["medium_term"].append("Deepen expertise in 2-3 core technologies")
        recommendations["medium_term"].append("Mentor junior developers to build leadership skills")
    else:
        recommendations["medium_term"].append("Prepare for system design interviews")
        recommendations["medium_term"].append("Lead a small project or feature end-to-end")
    
    # Long-term goals (6-12 months)
    if match_score < 70:
        recommendations["long_term"].append("Target mid-level roles after skill gap closure")
        recommendations["long_term"].append("Build a portfolio of 5+ significant projects")
    else:
        recommendations["long_term"].append("Aim for senior-level positions or technical lead roles")
        recommendations["long_term"].append("Develop domain expertise in your target industry")
    
    return recommendations