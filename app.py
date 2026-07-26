import streamlit as st
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import InferenceClient
import re

# Page Config
st.set_page_config(page_title="AI Career & Resume Coach", page_icon="🤖", layout="wide")

st.title("🤖 AI Resume & Career Coach (Powered by LLMs)")
st.write("Upload your resume and job description to get instant AI Feedback, Skill Gaps & Resume Rewrite Tips!")

# Sidebar for API Configuration
st.sidebar.header("🔑 API Configuration")
hf_token = st.sidebar.text_input("Enter Hugging Face Token", type="password", help="Get free token from huggingface.co/settings/tokens")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "
    return text

# Function to call LLM for AI Recommendations
def get_ai_feedback(resume_text, jd_text, token):
    try:
        # Free Inference Client using Hugging Face Hub
        client = InferenceClient(token=token)
        
        prompt = f"""
        You are an expert HR Specialist and ATS Career Coach. 
        Analyze the following Resume against the Job Description.

        --- RESUME TEXT ---
        {resume_text[:2000]}

        --- JOB DESCRIPTION ---
        {jd_text[:2000]}

        Please provide feedback in clear Markdown with these specific sections:
        1. **Top Strengths:** What matches well between the resume and JD?
        2. **Critical Skill Gaps:** What missing skills or keywords must be added?
        3. **Actionable Suggestions to Rewrite Resume:** Give 2 specific bullet point rewrites to improve ATS score.
        """
        
        # Calling chat completions using an open model
        response = client.chat_completion(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not fetch AI feedback. Check your API token or connection. Error: {str(e)}"

# Main Input Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste Job Description here...", height=230)

# Execution
if st.button("Run AI Deep Analysis 🚀", type="primary"):
    if uploaded_file is not None and job_description.strip() != "":
        with st.spinner("Extracting text and calculating match..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            # 1. Cosine Similarity Match Score
            text_list = [resume_text, job_description]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(text_list)
            
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            match_percentage = round(similarity_matrix[0][0] * 100, 2)
            
        st.divider()
        st.subheader("📊 Match Score Metrics")
        st.metric(label="ATS Match Percentage", value=f"{match_percentage}%")
        
        # 2. LLM AI Feedback Block
        st.divider()
        st.subheader("💡 Deep AI Recommendations & Action Plan")
        
        if hf_token:
            with st.spinner("Asking AI Model for detailed recommendations..."):
                ai_analysis = get_ai_feedback(resume_text, job_description, hf_token)
                st.markdown(ai_analysis)
        else:
            st.warning("👈 Please enter your **Hugging Face Token** in the sidebar to generate AI Insights!")
            
    else:
        st.error("Please upload a PDF resume AND paste a job description!")