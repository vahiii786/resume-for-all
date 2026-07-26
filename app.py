import streamlit as st
import re
from collections import Counter
import math

st.set_page_config(page_title="AI Resume Matcher", page_icon="📄", layout="wide")

st.title("📄 Smart AI Resume & Skill Gap Analyzer")
st.write("Analyze your resume alignment against job descriptions using pure NLP matching.")

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
    
    stop_words = {'and', 'the', 'for', 'with', 'you', 'this', 'that', 'from', 'have', 'will', 'are', 'your', 'our', 'work', 'experience', 'this', 'that'}
    
    jd_keywords = clean_jd - stop_words
    resume_keywords = clean_resume - stop_words
    
    missing_keywords = list(jd_keywords - resume_keywords)
    return missing_keywords[:12]

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Paste Resume Text")
    resume_text = st.text_area("Paste your Resume content here...", height=230)

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste Job Description here...", height=230)

if st.button("Analyze Resume & Find Gaps 🚀", type="primary"):
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
                st.success("🎯 Excellent Alignment!")
            elif match_percentage >= 25:
                st.warning("⚠️ Moderate Alignment.")
            else:
                st.error("❌ Low Alignment.")
                
        with m_col2:
            st.write("**Top Missing Keywords in Resume:**")
            if missing_skills:
                st.write(", ".join([f"`{word}`" for word in missing_skills]))
            else:
                st.write("🎉 Good job! Almost all major keywords exist in your resume.")
                
    else:
        st.error("Please paste BOTH Resume and Job Description!")
