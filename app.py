import streamlit as st
import re
from collections import Counter
import math
import urllib.parse

# Safe Imports
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

st.set_page_config(
    page_title="AI Resume Suite & Career Hub",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Smart AI Resume Hub & All-in-One Career Suite")

# Navigation Tabs (All 7 Features Included)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Resume Analyzer & Jobs", 
    "✏️ Live Resume Builder",
    "✨ AI Bullet Rewriter",
    "🎯 Keyword Placement & Red Flags", 
    "💰 Salary Predictor", 
    "✉️ HR Cold Outreach", 
    "🎤 AI Mock Interview"
])

# Shared Helper Functions
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

# Helper to format URL for redirection
def format_url(url):
    url = url.strip()
    if not url:
        return ""
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url

# Helper to render text with clean Bullet Points for Sub-points
def format_bullet_points(text):
    if not text.strip():
        return ""
    lines = text.strip().split('\n')
    html_out = ""
    in_list = False
    
    for line in lines:
        line_str = line.strip()
        if line_str.startswith("- ") or line_str.startswith("* ") or line_str.startswith("• "):
            if not in_list:
                html_out += "<ul style='margin: 4px 0 8px 18px; padding-left: 0; list-style-type: disc;'>"
                in_list = True
            clean_line = line_str.lstrip("-*• ").strip()
            html_out += f"<li style='margin-bottom: 3px; font-size: 12.5px;'>{clean_line}</li>"
        else:
            if in_list:
                html_out += "</ul>"
                in_list = False
            html_out += f"<p style='font-size: 12.5px; margin-bottom: 4px;'>{line_str}</p>"
            
    if in_list:
        html_out += "</ul>"
        
    return html_out

# Sidebar Inputs (Global)
st.sidebar.header("📥 Upload Documents")
resume_file = st.sidebar.file_uploader("Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
resume_text_input = st.sidebar.text_area("OR Paste Resume Text", height=150)
extracted_resume = extract_text_from_file(resume_file)
resume_text = extracted_resume if extracted_resume.strip() != "" else resume_text_input

jd_file = st.sidebar.file_uploader("Upload Job Description (.txt, .pdf, .docx)", type=["pdf", "docx", "txt"])
jd_text_input = st.sidebar.text_area("OR Paste JD Text", height=150)
extracted_jd = extract_text_from_file(jd_file)
job_description = extracted_jd if extracted_jd.strip() != "" else jd_text_input

# ==================== TAB 1: RESUME ANALYZER & JOBS ====================
with tab1:
    st.subheader("📊 Match Score & Live Job Recommendations")
    if st.button("Run Full Analysis 🚀", type="primary"):
        if resume_text.strip() != "" and job_description.strip() != "":
            v1 = text_to_vector(resume_text)
            v2 = text_to_vector(job_description)
            match_percentage = round(get_cosine_similarity(v1, v2) * 100, 2)
            missing_skills = get_missing_keywords(resume_text, job_description)
            target_role = extract_job_title(job_description)
            encoded_role = urllib.parse.quote(target_role)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Match Score Percentage", value=f"{match_percentage}%")
                if match_percentage >= 50:
                    st.success("🎯 High Match Alignment!")
                elif match_percentage >= 25:
                    st.warning("⚠️ Moderate Alignment. Needs improvement.")
                else:
                    st.error("❌ Low Alignment.")
            with col2:
                st.write("**Missing Keywords:**")
                st.write(", ".join([f"`{w}`" for w in missing_skills]) if missing_skills else "None! Excellent Job.")

            st.divider()
            st.subheader(f"💼 Live Job Openings: {target_role}")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.link_button("Apply on LinkedIn 🚀", f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}", use_container_width=True)
            with c2:
                st.link_button("Apply on Naukri 🚀", f"https://www.naukri.com/{encoded_role.replace('%20', '-')}-jobs", use_container_width=True)
            with c3:
                st.link_button("Apply on Indeed 🚀", f"https://www.indeed.com/jobs?q={encoded_role}", use_container_width=True)
        else:
            st.error("Please upload/paste both Resume and Job Description in the Sidebar!")

# ==================== TAB 2: LIVE RESUME BUILDER ====================
with tab2:
    st.subheader("✏️ Build & Edit Your ATS Resume")
    
    theme_choice = st.radio("🎨 Choose Resume Theme:", ["Modern Blue", "Executive Gold/Black", "Minimal Dark Header"], horizontal=True)

    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("### 📝 Enter Details")
        full_name = st.text_input("Full Name", "Your Full Name")
        title = st.text_input("Professional Title", "Data Science / Developer")
        email = st.text_input("Email", "yourname@email.com")
        phone = st.text_input("Phone", "+91 9876543210")
        location = st.text_input("Location", "Bhimavaram, India")
        linkedin = st.text_input("LinkedIn Profile URL", "https://www.linkedin.com/in/yourprofile")
        github = st.text_input("GitHub Profile URL", "https://github.com/yourusername")

        st.markdown("---")
        st.caption("💡 *Tip: Start sub-points with a dash (`- `) or star (`* `) to automatically convert them into clean bullet points!*")
        objective = st.text_area("Career Objective", "")
        education = st.text_area("Education", "- B.Sc Computer Science | Aditya Degree College (2023 - 2026)\n- Higher Secondary | Narayana Junior College (2020 - 2022)")
        skills = st.text_area("Technical Skills", "- Languages: C, Java, Python\n- Databases: DBMS, SQL\n- Fundamentals: Algorithms, Data Structures")
        certifications = st.text_area("Certifications (Optional)", "- Cisco Certification: C and Cybersecurity\n- Infosys Springboard: Computer Fundamentals & C")
        projects = st.text_area("Key Projects", "- Smart AI Resume Matcher\n  - Developed Streamlit app with ATS analysis.\n  - Embedded real-time job recommendation engines.")
        experience = st.text_area("Work / Internship Experience (Optional)", "")
        languages = st.text_area("Language Competencies", "- Telugu: Native\n- English: Fluent\n- Hindi: Conversational")
        hobbies = st.text_input("Interests / Hobbies (Optional)", "Reading Tech Blogs, Cooking, Problem Solving")
        
        st.markdown("---")
        declaration = st.text_area("Declaration Statement", "I hereby declare that all the information provided in the resume is true and accurate to the best of my knowledge.")
        dec_date = st.text_input("Date", "")

    with b_col2:
        st.markdown("### 👁️ Live Preview")
        
        # Theme Styles Logic
        if theme_choice == "Modern Blue":
            primary_color, title_color, header_bg = "#1E3A8A", "#4B5563", "transparent"
        elif theme_choice == "Executive Gold/Black":
            primary_color, title_color, header_bg = "#B45309", "#1F2937", "#FFFBEB"
        else: # Minimal Dark Header
            primary_color, title_color, header_bg = "#0F172A", "#64748B", "#F8FAFC"

        # Format Profile URLs for Redirection
        linkedin_url = format_url(linkedin)
        github_url = format_url(github)

        # Display exact text entered by user while being clickable
        contact_items = [f"📍 {location}", f"📞 {phone}", f"📧 {email}"]
        if linkedin.strip():
            contact_items.append(f"<a href='{linkedin_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{linkedin.strip()}</a>")
        if github.strip():
            contact_items.append(f"<a href='{github_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{github.strip()}</a>")
        
        contact_html = " &nbsp;|&nbsp; ".join(contact_items)

        # Dynamic Sections with Sub-point Formatting
        obj_s = f"<h3 style='color:{primary_color};'>Career Objective</h3>{format_bullet_points(objective)}" if objective.strip() else ""
        edu_s = f"<h3 style='color:{primary_color};'>Education</h3>{format_bullet_points(education)}" if education.strip() else ""
        skl_s = f"<h3 style='color:{primary_color};'>Technical Skills</h3>{format_bullet_points(skills)}" if skills.strip() else ""
        crt_s = f"<h3 style='color:{primary_color};'>Certifications</h3>{format_bullet_points(certifications)}" if certifications.strip() else ""
        prj_s = f"<h3 style='color:{primary_color};'>Projects</h3>{format_bullet_points(projects)}" if projects.strip() else ""
        exp_s = f"<h3 style='color:{primary_color};'>Experience / Internships</h3>{format_bullet_points(experience)}" if experience.strip() else ""
        lng_s = f"<h3 style='color:{primary_color};'>Language Competencies</h3>{format_bullet_points(languages)}" if languages.strip() else ""
        hob_s = f"<h3 style='color:{primary_color};'>Interests / Hobbies</h3><p>{hobbies}</p>" if hobbies.strip() else ""
        dec_s = f"<h3 style='color:{primary_color};'>Declaration</h3><p>{declaration}</p>" if declaration.strip() else ""

        html_resume = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Georgia&family=Calibri&display=swap');
            body {{ font-family: 'Calibri', Arial, sans-serif; margin: 0; padding: 10px; color: #222; }}
            .resume-card {{ background: #fff; border: 1px solid #ddd; padding: 25px; border-radius: 8px; }}
            .header-container {{ text-align: center; margin-bottom: 12px; background: {header_bg}; padding: 12px; border-radius: 6px; }}
            h1 {{ font-family: 'Georgia', serif; color: {primary_color}; margin: 0 0 4px 0; font-size: 26px; text-transform: uppercase; letter-spacing: 1px; }}
            .title {{ font-size: 15px; font-weight: bold; color: {title_color}; margin-bottom: 6px; }}
            .contact {{ font-size: 12px; color: #4B5563; }}
            hr {{ border: 0; border-top: 2px solid {primary_color}; margin-bottom: 15px; }}
            h3 {{ font-family: 'Georgia', serif; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e5e7eb; padding-bottom: 3px; margin-top: 14px; margin-bottom: 6px; }}
            p {{ font-size: 12.5px; line-height: 1.4; margin: 0; white-space: pre-line; }}
            .footer-table {{ width: 100%; margin-top: 20px; font-size: 12px; color: #555; }}
            a {{ text-decoration: none; word-break: break-all; }}
        </style>
        </head>
        <body>
            <div class="resume-card">
                <div class="header-container">
                    <h1>{full_name}</h1>
                    <div class="title">{title}</div>
                    <div class="contact">{contact_html}</div>
                </div>
                <hr>
                
                {obj_s} {edu_s} {skl_s} {crt_s} {prj_s} {exp_s} {lng_s} {hob_s} {dec_s}
                
                <table class="footer-table">
                    <tr>
                        <td><strong>Location:</strong> {location}</td>
                        <td style="text-align: right;"><strong>Signature:</strong> {full_name}</td>
                    </tr>
                    <tr>
                        <td><strong>Date:</strong> {dec_date}</td>
                        <td></td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        st.markdown(html_resume, unsafe_allow_html=True)
        st.write("")
        st.download_button(
            label="📥 Download HTML Resume (Open & Press Ctrl+P for PDF)",
            data=html_resume,
            file_name=f"{full_name.replace(' ', '_')}_Resume.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )

# ==================== TAB 3: AI BULLET REWRITER ====================
with tab3:
    st.subheader("✨ Action-Oriented Bullet Point Improver")
    st.write("Type a basic bullet point below to generate high-impact ATS alternatives:")
    
    raw_bullet = st.text_input("Enter a simple project line:", "I made a python app for analysis")
    
    if st.button("Enhance Bullet Point ✨"):
        if raw_bullet.strip():
            st.markdown("### 🌟 Suggested Action-Oriented Options:")
            st.info("👉 **Option 1 (Metric Focused):** 'Architected and deployed a Python application, improving data processing and operational efficiency by 25%.'")
            st.success("👉 **Option 2 (Action Focused):** 'Spearheaded the design and implementation of an end-to-end Python pipeline to analyze key metrics.'")
            st.warning("👉 **Option 3 (Technical Focus):** 'Engineered a high-performance Python application utilizing optimized data structures for real-time analysis.'")
        else:
            st.warning("Please enter a sentence first!")

# ==================== TAB 4: SMART PLACEMENT & RED FLAGS ====================
with tab4:
    st.subheader("💡 ATS Keyword Placement & Red Flag Detector")
    if resume_text.strip() != "" and job_description.strip() != "":
        missing = get_missing_keywords(resume_text, job_description)
        
        st.markdown("### 📍 Where to Add Missing Keywords?")
        if missing:
            for i, kw in enumerate(missing[:6]):
                st.info(f"**Keyword:** `{kw.capitalize()}` ➔ **Suggested Bullet:** *'Successfully utilized {kw} in hands-on projects to improve workflow and optimization.'* (Add to **Skills/Projects** section)")
        else:
            st.success("No critical keywords missing!")

        st.divider()
        st.markdown("### 🚩 Resume Weakness & Cliché Detector")
        cliches = ['hardworking', 'honest', 'team player', 'self motivated', 'go getter', 'fast learner']
        found_cliches = [c for c in cliches if c in resume_text.lower()]
        
        if found_cliches:
            st.warning(f"⚠️ Found Overused Buzzwords: {', '.join(found_cliches)}")
            st.write("👉 **Replace them with Action Words:** `Spearheaded`, `Engineered`, `Optimized`, `Implemented`.")
        else:
            st.success("✅ Clean Resume! No weak or cliché buzzwords detected.")
    else:
        st.info("Upload Resume & JD in Sidebar to see Placement Suggestions!")

# ==================== TAB 5: SALARY PREDICTOR ====================
with tab5:
    st.subheader("💰 Market Experience & Salary Range Predictor")
    if job_description.strip() != "":
        target_role = extract_job_title(job_description)
        exp_match = re.search(r'(\d+)\+?\s*(years|yrs)', job_description.lower())
        exp_years = int(exp_match.group(1)) if exp_match else 2
        
        base_pay = 4 + (exp_years * 2.5)
        max_pay = base_pay + 5
        
        st.write(f"**Target Role:** `{target_role}`")
        st.write(f"**Estimated Experience Required:** `{exp_years}+ Years`")
        st.metric("Predicted Annual Package (India Market)", f"₹{base_pay:.1f} LPA - ₹{max_pay:.1f} LPA")
    else:
        st.info("Upload Job Description in Sidebar to Predict Salary Range!")

# ==================== TAB 6: HR COLD OUTREACH ====================
with tab6:
    st.subheader("✉️ HR Cold Email & LinkedIn Message Generator")
    if resume_text.strip() != "" and job_description.strip() != "":
        target_role = extract_job_title(job_description)
        
        st.markdown("### 💼 LinkedIn Direct Connection Request")
        linkedin_msg = f"Hi [Hiring Manager Name], I came across the {target_role} opening. With hands-on experience in relevant tools and a strong background matching your JD, I'd love to connect!"
        st.code(linkedin_msg, language="text")

        st.markdown("### 📧 Email Cold Outreach Draft")
        email_msg = f"Subject: Application for {target_role} Position - [Your Name]\n\nDear Hiring Manager,\n\nI noticed the opening for {target_role} and wanted to reach out directly. My technical skills align well with your job description.\n\nBest regards,\n[Your Name]"
        st.code(email_msg, language="text")
    else:
        st.info("Upload Resume & JD in Sidebar to Generate Outreach Messages!")

# ==================== TAB 7: MOCK INTERVIEW ====================
with tab7:
    st.subheader("🎤 AI Technical Mock Interview Practice")
    if job_description.strip() != "":
        target_role = extract_job_title(job_description)
        st.write(f"Practice top interview questions tailored for **{target_role}**:")

        q1 = f"1. How have you applied technical skills for {target_role} in your previous projects?"
        q2 = "2. Describe a challenging bug you resolved recently."

        st.write(q1)
        ans1 = st.text_area("Your Response for Question 1:", key="q1")
        
        st.write(q2)
        ans2 = st.text_area("Your Response for Question 2:", key="q2")

        if st.button("Evaluate Answers 📝"):
            if ans1.strip() != "" or ans2.strip() != "":
                st.success("✅ **AI Feedback:** Good structure! Mention specific metric improvements (e.g., *'Improved speed by 20%'*) to make it even stronger!")
            else:
                st.warning("Please type your answers first!")
    else:
        st.info("Upload Job Description in Sidebar to Start Mock Interview!")
