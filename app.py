import streamlit as st
import re
from collections import Counter
import math
import urllib.parse

st.set_page_config(page_title="AI Resume Matcher & Career Hub", page_icon="📄", layout="wide")

st.title("📄 Smart AI Resume Matcher & Job Assistant")
st.write("Analyze your resume, find skill gaps, get instant Job search links, and generate a custom Cover Letter!")

# Pure Python Cosine Similarity function
def text_to_vector(text):
    words = re.findall(r'\w+', text.lower())
    return Counter(words)

def get_cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x]**2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def get_missing_keywords(resume_text, jd_text):
    clean_resume = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
    clean_jd = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_text.lower()))
    
    stop_words = {'and', 'the', 'for', 'with', 'you', 'this', 'that', 'from', 'have', 'will', 'are', 'your', 'our', 'work', 'experience', 'looking', 'role', 'team', 'company', 'required', 'skills', 'good', 'must'}
    
    jd_keywords = clean_jd - stop_words
    resume_keywords = clean_resume - stop_words
    
    missing_keywords = list(jd_keywords - resume_keywords)
    return missing_keywords[:12]

# Extract potential Job Title from JD
def extract_job_title(jd_text):
    lines = jd_text.strip().split('\n')
    for line in lines[:3]:  # Check first few lines
        if "title" in line.lower() or "role" in line.lower() or "engineer" in line.lower() or "analyst" in line.lower() or "developer" in line.lower():
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', line)
            return clean.strip()
    return "Software Engineer"  # Default search query

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Paste Resume Text")
    resume_text = st.text_area("Paste your Resume content here...", height=230)

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste Job Description here...", height=230)

if st.button("Analyze Resume & Generate Insights 🚀", type="primary"):
    if resume_text.strip() != "" and job_description.strip() != "":
        v1 = text_to_vector(resume_text)
        v2 = text_to_vector(job_description)
        
        similarity = get_cosine_similarity(v1, v2)
        match_percentage = round(similarity * 100, 2)
        
        missing_skills = get_missing_keywords(resume_text, job_description)
        
        st.divider()
        st.subheader("📊 Analysis Summary")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Match Score Percentage", value=f"{match_percentage}%")
            if match_percentage >= 50:
                st.success("🎯 Excellent Alignment! You have high chances for this role.")
            elif match_percentage >= 25:
                st.warning("⚠️ Moderate Alignment. Adding missing keywords will boost your ATS score.")
            else:
                st.error("❌ Low Alignment. Consider updating skills or targeting a different role.")
                
        with m_col2:
            st.write("**Top Missing Keywords in Resume:**")
            if missing_skills:
                st.write(", ".join([f"`{word}`" for word in missing_skills]))
            else:
                st.write("🎉 Good job! Almost all major keywords exist in your resume.")
                
        # --- FEATURE 1: DYNAMIC JOB SEARCH LINKS ---
        st.divider()
        st.subheader("💼 Apply & Find Matching Jobs")
        
        target_role = extract_job_title(job_description)
        encoded_role = urllib.parse.quote(target_role)
        
        st.write(f"Based on this Job Description, we searched for roles matching **'{target_role}'**:")
        
        job_col1, job_col2, job_col3 = st.columns(3)
        
        with job_col1:
            linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}"
            st.link_button("🔍 Find on LinkedIn Jobs", linkedin_url)
            
        with job_col2:
            naukri_url = f"https://www.naukri.com/{encoded_role.replace('%20', '-')}-jobs"
            st.link_button("🔍 Search on Naukri.com", naukri_url)
            
        with job_col3:
            indeed_url = f"https://www.indeed.com/jobs?q={encoded_role}"
            st.link_button("🔍 Search on Indeed", indeed_url)
            
        # --- FEATURE 2: INSTANT COVER LETTER GENERATOR ---
        st.divider()
        st.subheader("✉️ Instant Tailored Cover Letter")
        
        extracted_skills = ", ".join(list(set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text)) - {'with', 'have', 'from', 'your', 'this', 'that'})[:6])
        
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the open role described in your job posting. With a strong background in hands-on technical execution and domain expertise in key areas such as {extracted_skills}, I am confident in my ability to make an immediate impact on your team.

My experience closely matches your requirements. I have a proven track record of solving technical challenges, working with cross-functional teams, and quickly learning new technologies to drive results.

I am eager to bring my skills to your organization and would welcome the opportunity to discuss how my background aligns with your team's goals. Thank you for your time and consideration.

Sincerely,
[Your Full Name]
[Your Contact Information]
"""
        st.text_area("Copy your generated Cover Letter below:", cover_letter, height=220)
        
    else:
        st.error("Please paste BOTH Resume and Job Description!")
