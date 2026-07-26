import streamlit as st
import re
from collections import Counter
import math
import urllib.parse

st.set_page_config(page_title="AI Resume Matcher & Career Hub", page_icon="📄", layout="wide")

st.title("📄 Smart AI Resume Matcher & Job Assistant")
st.write("Analyze your resume, find skill gaps, get live job recommendations, and generate a custom Cover Letter!")

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
    for line in lines[:5]:  # Check first few lines
        if any(term in line.lower() for term in ["title", "role", "engineer", "analyst", "developer", "designer", "manager"]):
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', line)
            return clean.strip()
    return "Data Analyst / Software Developer"

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Paste Resume Text")
    resume_text = st.text_area("Paste your Resume content here...", height=230)

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste Job Description here...", height=230)

if st.button("Analyze Resume & Find Opportunities 🚀", type="primary"):
    if resume_text.strip() != "" and job_description.strip() != "":
        v1 = text_to_vector(resume_text)
        v2 = text_to_vector(job_description)
        
        similarity = get_cosine_similarity(v1, v2)
        match_percentage = round(similarity * 100, 2)
        
        missing_skills = get_missing_keywords(resume_text, job_description)
        target_role = extract_job_title(job_description)
        encoded_role = urllib.parse.quote(target_role)

        st.divider()
        st.subheader("📊 Analysis Summary")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Match Score Percentage", value=f"{match_percentage}%")
            if match_percentage >= 50:
                st.success("🎯 Excellent Alignment! High chances of getting shortlisted.")
            elif match_percentage >= 25:
                st.warning("⚠️ Moderate Alignment. Add missing keywords to boost your ATS score.")
            else:
                st.error("❌ Low Alignment. Re-align skills or target a different role.")
                
        with m_col2:
            st.write("**Top Missing Keywords in Resume:**")
            if missing_skills:
                st.write(", ".join([f"`{word}`" for word in missing_skills]))
            else:
                st.write("🎉 Good job! Almost all major keywords exist in your resume.")
                
        # --- NEW FEATURE: LIVE AVAILABLE JOBS CARDS ---
        st.divider()
        st.subheader(f"💼 Live Job Openings for Domain: '{target_role}'")
        st.write("Click on any job card below to apply directly on live hiring platforms:")

        # Creating Live Dynamic Job Cards
        card1, card2, card3 = st.columns(3)

        with card1:
            with st.container(border=True):
                st.markdown(f"### 🏢 {target_role}")
                st.write("**Platform:** LinkedIn Jobs")
                st.write("**Location:** India / Remote")
                st.write("**Status:** 🔥 Actively Hiring")
                linkedin_link = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}"
                st.link_button("Apply Now on LinkedIn 🚀", linkedin_link, use_container_width=True)

        with card2:
            with st.container(border=True):
                st.markdown(f"### 💻 Senior / Mid {target_role}")
                st.write("**Platform:** Naukri.com")
                st.write("**Location:** Bangalore / Hyderabad / Remote")
                st.write("**Status:** ⚡ Fast Response")
                naukri_link = f"https://www.naukri.com/{encoded_role.replace('%20', '-')}-jobs"
                st.link_button("Apply Now on Naukri 🚀", naukri_link, use_container_width=True)

        with card3:
            with st.container(border=True):
                st.markdown(f"### 🌐 Urgent Opening: {target_role}")
                st.write("**Platform:** Indeed Jobs")
                st.write("**Location:** Pan India")
                st.write("**Status:** 🆕 Posted Recently")
                indeed_link = f"https://www.indeed.com/jobs?q={encoded_role}"
                st.link_button("Apply Now on Indeed 🚀", indeed_link, use_container_width=True)

        # --- FEATURE: INSTANT COVER LETTER GENERATOR ---
        st.divider()
        st.subheader("✉️ Auto-Generated Custom Cover Letter")
        
        extracted_skills = ", ".join(list(set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text)) - {'with', 'have', 'from', 'your', 'this', 'that'})[:6])
        
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {target_role} position. With a solid foundation in {extracted_skills}, I am confident in my ability to contribute effectively to your team's upcoming projects.

My hands-on experience directly matches the skills highlighted in your job description. I pride myself on solving technical problems efficiently and learning new tools rapidly to deliver impactful outcomes.

I welcome the opportunity to discuss how my skill set aligns with your organizational requirements. Thank you for considering my application.

Sincerely,
[Your Name]
[Your Contact Details]
"""
        st.text_area("Copy your Cover Letter:", cover_letter, height=200)
        
    else:
        st.error("Please paste BOTH Resume and Job Description!")
