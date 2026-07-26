import streamlit as st
import re
from collections import Counter
import math
import urllib.parse
import io

# Safe Imports for Resume Reading
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None

try:
    import docx
except ImportError:
    docx = None

# PDF Generator Library (reportlab)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

st.set_page_config(page_title="AI Resume Hub & Builder", page_icon="📄", layout="wide")

st.title("📄 Smart AI Resume Matcher & Career Hub")

# Tabs Navigation
tab1, tab2 = st.tabs(["📊 Resume Analyzer & Jobs", "✏️ Live Resume Builder / Editor"])

# ==================== TAB 1: ANALYZER & JOBS ====================
with tab1:
    st.write("Upload or paste your Resume and Job Description to get instant match score, missing skills, live job search links, and custom cover letters!")

    def extract_text_from_file(uploaded_file):
        if uploaded_file is None:
            return ""
        file_type = uploaded_file.name.split('.')[-1].lower()
        text = ""
        if file_type == "pdf" and PdfReader is not None:
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception:
                pass
        elif file_type in ["docx", "doc"] and docx is not None:
            try:
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception:
                pass
        elif file_type in ["txt", "md"]:
            try:
                text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            except Exception:
                text = ""
        return text

    def text_to_vector(text):
        words = re.findall(r'\w+', text.lower())
        return Counter(words)

    def get_cosine_similarity(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in list(vec1.keys())])
        sum2 = sum([vec2[x]**2 for x in list(vec2.keys())])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        return float(numerator) / denominator if denominator else 0.0

    def get_missing_keywords(resume_text, jd_text):
        clean_resume = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
        clean_jd = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_text.lower()))
        stop_words = {'and', 'the', 'for', 'with', 'you', 'this', 'that', 'from', 'have', 'will', 'are', 'your', 'our', 'work', 'experience', 'looking', 'role', 'team', 'company', 'required', 'skills', 'good', 'must'}
        return list((clean_jd - stop_words) - (clean_resume - stop_words))[:12]

    def extract_job_title(jd_text):
        lines = jd_text.strip().split('\n')
        for line in lines[:5]:
            if any(term in line.lower() for term in ["title", "role", "engineer", "analyst", "developer", "designer", "manager"]):
                return re.sub(r'[^a-zA-Z0-9\s]', '', line).strip()
        return "Software Developer"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Resume Input")
        resume_file = st.file_uploader("Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
        resume_text_input = st.text_area("OR Paste Resume Text here...", height=150)
        extracted_resume = extract_text_from_file(resume_file)
        resume_text = extracted_resume if extracted_resume.strip() != "" else resume_text_input

    with col2:
        st.subheader("2. Job Description Input")
        jd_file = st.file_uploader("Upload Job Description (.txt, .pdf, .docx)", type=["pdf", "docx", "txt"])
        jd_text_input = st.text_area("OR Paste Job Description here...", height=150)
        extracted_jd = extract_text_from_file(jd_file)
        job_description = extracted_jd if extracted_jd.strip() != "" else jd_text_input

    if st.button("Analyze Resume & Find Opportunities 🚀", type="primary"):
        if resume_text.strip() != "" and job_description.strip() != "":
            v1 = text_to_vector(resume_text)
            v2 = text_to_vector(job_description)
            match_percentage = round(get_cosine_similarity(v1, v2) * 100, 2)
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

            # Live Job Cards
            st.divider()
            st.subheader(f"💼 Live Job Openings for Domain: '{target_role}'")
            card1, card2, card3 = st.columns(3)
            with card1:
                with st.container(border=True):
                    st.markdown(f"### 🏢 {target_role}")
                    st.write("**Platform:** LinkedIn Jobs")
                    st.link_button("Apply Now on LinkedIn 🚀", f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}", use_container_width=True)
            with card2:
                with st.container(border=True):
                    st.markdown(f"### 💻 Senior / Mid {target_role}")
                    st.write("**Platform:** Naukri.com")
                    st.link_button("Apply Now on Naukri 🚀", f"https://www.naukri.com/{encoded_role.replace('%20', '-')}-jobs", use_container_width=True)
            with card3:
                with st.container(border=True):
                    st.markdown(f"### 🌐 Urgent Opening: {target_role}")
                    st.write("**Platform:** Indeed Jobs")
                    st.link_button("Apply Now on Indeed 🚀", f"https://www.indeed.com/jobs?q={encoded_role}", use_container_width=True)

            # Auto Cover Letter
            st.divider()
            st.subheader("✉️ Auto-Generated Custom Cover Letter")
            extracted_skills = ", ".join(list(set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text)) - {'with', 'have', 'from', 'your', 'this', 'that'})[:6])
            cover_letter = f"""Dear Hiring Manager,\n\nI am writing to express my strong interest in the {target_role} position. With a solid foundation in {extracted_skills}, I am confident in my ability to contribute effectively to your team.\n\nMy hands-on experience directly matches the skills highlighted in your job description.\n\nSincerely,\n[Your Name]"""
            st.text_area("Copy your Cover Letter:", cover_letter, height=160)
        else:
            st.error("Please provide BOTH Resume and Job Description!")

# ==================== TAB 2: LIVE RESUME BUILDER & EDITOR ====================
with tab2:
    st.subheader("✏️ Build & Customize Your Professional ATS Resume")
    st.write("Fill in your details below to instantly generate a formatted, ATS-friendly resume!")

    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("### 📝 Input Your Details")
        full_name = st.text_input("Full Name", "John Doe")
        title = st.text_input("Professional Title", "Full Stack Python Developer")
        email = st.text_input("Email", "johndoe@email.com")
        phone = st.text_input("Phone", "+91 9876543210")
        location = st.text_input("Location", "Hyderabad, India")
        linkedin = st.text_input("LinkedIn Profile", "linkedin.com/in/johndoe")

        st.markdown("---")
        summary = st.text_area("Professional Summary", "Results-driven Software Developer with experience in building scalable web applications and AI solutions.")
        skills = st.text_area("Technical Skills (comma-separated)", "Python, Streamlit, SQL, Git, REST APIs, HTML/CSS")
        experience = st.text_area("Work Experience", "Software Developer | Tech Corp (2022 - Present)\n- Developed AI tools improving efficiency by 30%.\n- Integrated REST APIs for dynamic job searches.")
        education = st.text_area("Education", "B.Tech in Computer Science | JNTU (2018 - 2022)")
        projects = st.text_area("Key Projects", "AI Resume Assistant & Career Hub\n- Built a Streamlit web app for resume analysis and live job matching.")

    with b_col2:
        st.markdown("### 👁️ Live Resume Preview")
        
        # HTML/CSS Template for Screen Preview
        resume_template = f"""
        <div style="background-color:#ffffff; color:#000000; padding:25px; border-radius:8px; border:1px solid #ddd; font-family:Arial, sans-serif;">
            <h1 style="margin:0; color:#1E3A8A; font-size:26px;">{full_name}</h1>
            <p style="font-size:16px; font-weight:bold; color:#4B5563; margin-top:5px;">{title}</p>
            <p style="font-size:12px; color:#6B7280;">📧 {email} | 📞 {phone} | 📍 {location} | 🌐 {linkedin}</p>
            <hr style="border:0.5px solid #1E3A8A;">
            
            <h3 style="color:#1E3A8A; margin-bottom:5px;">Professional Summary</h3>
            <p style="font-size:13px; line-height:1.4;">{summary}</p>
            
            <h3 style="color:#1E3A8A; margin-bottom:5px;">Technical Skills</h3>
            <p style="font-size:13px; line-height:1.4;">{skills}</p>
            
            <h3 style="color:#1E3A8A; margin-bottom:5px;">Work Experience</h3>
            <p style="font-size:13px; line-height:1.4; white-space: pre-line;">{experience}</p>
            
            <h3 style="color:#1E3A8A; margin-bottom:5px;">Projects</h3>
            <p style="font-size:13px; line-height:1.4; white-space: pre-line;">{projects}</p>
            
            <h3 style="color:#1E3A8A; margin-bottom:5px;">Education</h3>
            <p style="font-size:13px; line-height:1.4; white-space: pre-line;">{education}</p>
        </div>
        """
        st.markdown(resume_template, unsafe_allow_html=True)
        st.write("")

        # PDF Generator Function
        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            name_style = ParagraphStyle('NameStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor("#1E3A8A"), spaceAfter=2)
            title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#4B5563"), spaceAfter=4)
            contact_style = ParagraphStyle('ContactStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#6B7280"), spaceAfter=10)
            heading_style = ParagraphStyle('HeadingStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
            body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.black, leading=14, spaceAfter=8)

            story = []
            
            # Header
            story.append(Paragraph(full_name, name_style))
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(f"{email} | {phone} | {location} | {linkedin}", contact_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=10))

            # Sections
            story.append(Paragraph("Professional Summary", heading_style))
            story.append(Paragraph(summary.replace('\n', '<br/>'), body_style))

            story.append(Paragraph("Technical Skills", heading_style))
            story.append(Paragraph(skills.replace('\n', '<br/>'), body_style))

            story.append(Paragraph("Work Experience", heading_style))
            story.append(Paragraph(experience.replace('\n', '<br/>'), body_style))

            story.append(Paragraph("Key Projects", heading_style))
            story.append(Paragraph(projects.replace('\n', '<br/>'), body_style))

            story.append(Paragraph("Education", heading_style))
            story.append(Paragraph(education.replace('\n', '<br/>'), body_style))

            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        # Download PDF Button
        if REPORTLAB_AVAILABLE:
            pdf_bytes = generate_pdf()
            st.download_button(
                label="📥 Download Professional Resume (PDF)",
                data=pdf_bytes,
                file_name=f"{full_name.replace(' ', '_')}_Resume.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.error("ReportLab library not installed. PDF generation is temporarily unavailable.")
