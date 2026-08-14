import streamlit as st
import re
from collections import Counter
import math
import urllib.parse
from PIL import Image

# Multi-level PDF & File Extraction Libraries
fitz_available = False
try:
    import fitz  # PyMuPDF
    fitz_available = True
except ImportError:
    fitz_available = False

pdfplumber_available = False
try:
    import pdfplumber
    pdfplumber_available = True
except ImportError:
    pdfplumber_available = False

pypdf_available = False
try:
    import pypdf
    pypdf_available = True
except ImportError:
    pypdf_available = False

docx_available = False
try:
    import docx
    docx_available = True
except ImportError:
    docx_available = False

ocr_available = False
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    ocr_available = True
except ImportError:
    ocr_available = False

st.set_page_config(
    page_title="AI Resume Suite & Career Hub",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Smart AI Resume Hub & All-in-One Career Suite")

# Global Session State
if "built_resume_text" not in st.session_state:
    st.session_state["built_resume_text"] = ""

# All 7 Tabs Preserved
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Resume Analyzer & Jobs", 
    "✏️ Live Resume Builder",
    "✨ AI Bullet Rewriter",
    "🎯 Keyword Placement & Red Flags", 
    "💰 Salary Predictor", 
    "✉️ HR Cold Outreach", 
    "🎤 AI Mock Interview"
])

# 4-Layer Bulletproof Text Extractor
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = ""
    
    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        if file_type == "pdf":
            # Layer 1: PyMuPDF (Fastest for standard text PDFs)
            if fitz_available:
                try:
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    for page in doc:
                        extracted = page.get_text()
                        if extracted:
                            text += extracted + "\n"
                except Exception:
                    text = ""

            # Layer 2: pdfplumber fallback
            if not text.strip() and pdfplumber_available:
                try:
                    uploaded_file.seek(0)
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            extracted = page.extract_text()
                            if extracted:
                                text += extracted + "\n"
                except Exception:
                    text = ""

            # Layer 3: pypdf fallback
            if not text.strip() and pypdf_available:
                try:
                    uploaded_file.seek(0)
                    reader = pypdf.PdfReader(uploaded_file)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                except Exception:
                    text = ""

            # Layer 4: OCR Engine for Scanned / Canva / Image PDFs
            if not text.strip() and ocr_available:
                try:
                    images = convert_from_bytes(file_bytes)
                    for img in images:
                        extracted = pytesseract.image_to_string(img)
                        if extracted:
                            text += extracted + "\n"
                except Exception:
                    text = ""

        elif file_type in ["docx", "doc"]:
            if docx_available:
                uploaded_file.seek(0)
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    if para.text:
                        text += para.text + "\n"

        elif file_type in ["txt", "md"]:
            text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            
    except Exception:
        pass
        
    return text.strip()

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

def format_url(url):
    url = url.strip()
    if not url:
        return ""
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url

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

# Sidebar Inputs
st.sidebar.header("📥 Upload Documents")
resume_file = st.sidebar.file_uploader("Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
resume_text_input = st.sidebar.text_area("OR Paste Resume Text", value=st.session_state["built_resume_text"], height=150)

extracted_resume = extract_text_from_file(resume_file)
resume_text = extracted_resume if extracted_resume != "" else resume_text_input

if resume_file:
    if extracted_resume != "":
        st.sidebar.success(f"✅ Loaded {len(extracted_resume.split())} words from Resume!")
    else:
        st.sidebar.warning("⚠️ Could not extract text. Please paste text in box below.")

st.sidebar.divider()

# Mandatory కాకుండా Optional JD Toggle
has_jd = st.sidebar.radio("Do you have a Job Description (JD) to match?", ["No (Check General Resume Score)", "Yes (Compare with Job Description)"])

job_description = ""
if has_jd == "Yes (Compare with Job Description)":
    jd_file = st.sidebar.file_uploader("Upload Job Description (.txt, .pdf, .docx)", type=["pdf", "docx", "txt"])
    jd_text_input = st.sidebar.text_area("OR Paste JD Text", height=150)

    extracted_jd = extract_text_from_file(jd_file)
    job_description = extracted_jd if extracted_jd != "" else jd_text_input

    if jd_file and extracted_jd != "":
        st.sidebar.success(f"✅ Loaded {len(extracted_jd.split())} words from JD!")
        
# General Resume Quality Calculator (When NO JD is provided)
def calculate_general_resume_score(text):
    score = 0
    feedback = []
    word_count = len(text.split())
    
    # 1. Word Count Check (Ideal: 250 - 1000 words)
    if 250 <= word_count <= 1000:
        score += 25
        feedback.append("✅ **Ideal Length:** Resume length is optimal for ATS readable scans.")
    elif word_count < 250:
        score += 10
        feedback.append("⚠️ **Too Short:** Resume might be lacking details. Aim for at least 300+ words.")
    else:
        score += 15
        feedback.append("⚠️ **Too Long:** Try to condense your resume to 1-2 pages.")

    # 2. Key Sections Check
    text_lower = text.lower()
    sections = ['education', 'skills', 'experience', 'projects']
    found_sections = [s for s in sections if s in text_lower]
    score += len(found_sections) * 10  # Max 40 points
    feedback.append(f"✅ **Essential Sections Found:** Found {len(found_sections)}/4 key sections ({', '.join([s.capitalize() for s in found_sections])}).")

    # 3. Action Verbs Check
    action_words = ['developed', 'managed', 'created', 'built', 'designed', 'implemented', 'led', 'improved', 'analyzed', 'engineered']
    found_verbs = [v for v in action_words if v in text_lower]
    if len(found_verbs) >= 4:
        score += 20
        feedback.append(f"✅ **Strong Action Verbs:** Good usage of power words like `{', '.join(found_verbs[:4])}`.")
    else:
        score += 10
        feedback.append("💡 **Action Verbs:** Consider adding more action words (e.g., *Built, Engineered, Developed*).")

    # 4. Contact/Links Check
    if any(k in text_lower for k in ['email', '@', 'linkedin', 'github', 'phone']):
        score += 15
        feedback.append("✅ **Contact Information:** Contact or portfolio details detected.")
    else:
        feedback.append("⚠️ **Contact Info Missing:** Ensure your email or phone number is clearly stated.")

    return score, feedback


# ==================== TAB 1: RESUME ANALYZER & JOBS ====================
with tab1:
    st.subheader("📊 Resume Score & Analysis")
    
    if st.button("Run Full Analysis 🚀", type="primary"):
        if resume_text.strip() == "":
            st.error("Please upload or paste your Resume first in the Sidebar!")
        else:
            # CASE 1: USER HAS A JOB DESCRIPTION (YES)
            if has_jd == "Yes (Compare with Job Description)" and job_description.strip() != "":
                v1 = text_to_vector(resume_text)
                v2 = text_to_vector(job_description)
                match_percentage = round(get_cosine_similarity(v1, v2) * 100, 2)
                missing_skills = get_missing_keywords(resume_text, job_description)
                target_role = extract_job_title(job_description)
                encoded_role = urllib.parse.quote(target_role)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="🎯 Job Match Score", value=f"{match_percentage}%")
                    if match_percentage >= 50:
                        st.success("🎯 High Match Alignment with Job Description!")
                    elif match_percentage >= 25:
                        st.warning("⚠️ Moderate Alignment. Needs improvement.")
                    else:
                        st.error("❌ Low Alignment. Add relevant missing keywords.")
                with col2:
                    st.write("**Missing Keywords from JD:**")
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

            # CASE 2: USER DOES NOT HAVE A JOB DESCRIPTION (NO)
            else:
                gen_score, feedback_list = calculate_general_resume_score(resume_text)
                
                st.metric(label="📈 General Resume Quality Score", value=f"{gen_score} / 100")
                
                if gen_score >= 75:
                    st.success("🌟 Excellent Resume Structure & ATS Readiness!")
                elif gen_score >= 50:
                    st.warning("⚠️ Good Resume, but can be improved further.")
                else:
                    st.error("❌ Low Score. Consider adding missing sections or content.")

                st.divider()
                st.markdown("### 🔍 ATS Quality Feedback Summary:")
                for item in feedback_list:
                    st.write(item)

# ==================== TAB 2: LIVE RESUME EDITOR & BUILDER ====================
with tab2:
    st.subheader("✏️ Resume Upload & Interactive Editor")
    st.write("అప్లోడ్ చేసిన రెజ్యూమ్‌లోని వివరాలను కింద ఉన్న బాక్సులలో నేరుగా ఎడిట్ లేదా మార్పులు చేసుకోవచ్చు.")
    
    # 1. File Upload to Edit
    uploaded_edit_file = st.file_uploader("📂 Upload Resume to Edit (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="editor_file")
    
    # State setup for dynamic editing
    if "ed_name" not in st.session_state: st.session_state["ed_name"] = "Your Full Name"
    if "ed_title" not in st.session_state: st.session_state["ed_title"] = "Professional Title"
    if "ed_email" not in st.session_state: st.session_state["ed_email"] = "email@example.com"
    if "ed_phone" not in st.session_state: st.session_state["ed_phone"] = "+91 9876543210"
    if "ed_loc" not in st.session_state: st.session_state["ed_loc"] = "City, Country"
    if "ed_obj" not in st.session_state: st.session_state["ed_obj"] = ""
    if "ed_edu" not in st.session_state: st.session_state["ed_edu"] = "- Degree | College Name (Year)"
    if "ed_skills" not in st.session_state: st.session_state["ed_skills"] = "- Technical Skills: Python, SQL..."
    if "ed_exp" not in st.session_state: st.session_state["ed_exp"] = ""
    if "ed_proj" not in st.session_state: st.session_state["ed_proj"] = "- Project Name: Description"
    if "ed_cert" not in st.session_state: st.session_state["ed_cert"] = ""

    if uploaded_edit_file is not None:
        if st.button("📥 Load Uploaded Text into Editor"):
            extracted_raw = extract_text_from_file(uploaded_edit_file)
            if extracted_raw:
                # Load extracted content into editable experience/raw state
                st.session_state["ed_exp"] = extracted_raw
                st.success("✅ Text loaded successfully! You can now edit/modify all text below.")
            else:
                st.error("Could not read text from this file. Try uploading a text-based PDF/DOCX.")

    st.divider()

    theme_choice = st.radio("🎨 Choose Resume Theme:", ["Modern Blue", "Executive Gold/Black", "Minimal Dark Header"], horizontal=True)

    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("### 📝 Edit Resume Sections")
        
        full_name = st.text_input("Full Name", st.session_state["ed_name"])
        title = st.text_input("Professional Title", st.session_state["ed_title"])
        email = st.text_input("Email", st.session_state["ed_email"])
        phone = st.text_input("Phone Number", st.session_state["ed_phone"])
        location = st.text_input("Location", st.session_state["ed_loc"])
        linkedin = st.text_input("LinkedIn Profile URL", "https://www.linkedin.com/in/")
        github = st.text_input("GitHub Profile URL", "https://github.com/")

        st.markdown("---")
        objective = st.text_area("Edit Objective / Summary", st.session_state["ed_obj"], height=100)
        skills = st.text_area("Edit Skills (Use - for bullet points)", st.session_state["ed_skills"], height=120)
        experience = st.text_area("Edit Work Experience / Raw Uploaded Content", st.session_state["ed_exp"], height=200)
        projects = st.text_area("Edit Projects", st.session_state["ed_proj"], height=120)
        education = st.text_area("Edit Education", st.session_state["ed_edu"], height=100)
        certifications = st.text_area("Edit Certifications (Optional)", st.session_state["ed_cert"], height=80)
        languages = st.text_area("Languages Spoken", "- English\n- Telugu")
        declaration = st.text_area("Declaration Statement", "I hereby declare that all information provided is accurate to the best of my knowledge.")
        dec_date = st.text_input("Date", "")

        # Sync edited content with Tab 1 (Analyzer)
        edited_full_text = f"{full_name}\n{title}\n{objective}\n{skills}\n{experience}\n{projects}\n{education}\n{certifications}"
        if st.button("🔄 Sync Edited Resume with Analyzer"):
            st.session_state["built_resume_text"] = edited_full_text
            st.success("✅ Changes synced! Go to Tab 1 to check ATS score of this updated resume.")

    with b_col2:
        st.markdown("### 👁️ Live Updated Preview")
        
        if theme_choice == "Modern Blue":
            primary_color, title_color, header_bg = "#1E3A8A", "#4B5563", "transparent"
        elif theme_choice == "Executive Gold/Black":
            primary_color, title_color, header_bg = "#B45309", "#1F2937", "#FFFBEB"
        else:
            primary_color, title_color, header_bg = "#0F172A", "#64748B", "#F8FAFC"

        linkedin_url = format_url(linkedin)
        github_url = format_url(github)

        contact_items = [f"📍 {location}", f"📞 {phone}", f"📧 {email}"]
        if linkedin.strip():
            contact_items.append(f"<a href='{linkedin_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{linkedin.strip()}</a>")
        if github.strip():
            contact_items.append(f"<a href='{github_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{github.strip()}</a>")
        
        contact_html = " &nbsp;|&nbsp; ".join(contact_items)

        obj_s = f"<h3 style='color:{primary_color};'>Career Objective</h3>{format_bullet_points(objective)}" if objective.strip() else ""
        edu_s = f"<h3 style='color:{primary_color};'>Education</h3>{format_bullet_points(education)}" if education.strip() else ""
        skl_s = f"<h3 style='color:{primary_color};'>Technical Skills</h3>{format_bullet_points(skills)}" if skills.strip() else ""
        crt_s = f"<h3 style='color:{primary_color};'>Certifications</h3>{format_bullet_points(certifications)}" if certifications.strip() else ""
        prj_s = f"<h3 style='color:{primary_color};'>Projects</h3>{format_bullet_points(projects)}" if projects.strip() else ""
        exp_s = f"<h3 style='color:{primary_color};'>Experience / Career History</h3>{format_bullet_points(experience)}" if experience.strip() else ""
        lng_s = f"<h3 style='color:{primary_color};'>Languages</h3>{format_bullet_points(languages)}" if languages.strip() else ""
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
                
                {obj_s} {skl_s} {exp_s} {prj_s} {edu_s} {crt_s} {lng_s} {dec_s}
                
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
            label="📥 Download Edited Resume (Press Ctrl+P for PDF)",
            data=html_resume,
            file_name=f"{full_name.replace(' ', '_')}_Edited_Resume.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )
# ==================== TAB 3: AI BULLET REWRITER ====================
with tab3:
    st.subheader("✨ Action-Oriented Bullet Point Improver")
    raw_bullet = st.text_input("Enter a simple project line:", "I made a python app for analysis")
    if st.button("Enhance Bullet Point ✨"):
        if raw_bullet.strip():
            st.markdown("### 🌟 Suggested Action-Oriented Options:")
            st.info("👉 **Option 1 (Metric Focused):** 'Architected and deployed a Python application, improving data processing and operational efficiency by 25%.'")
            st.success("👉 **Option 2 (Action Focused):** 'Spearheaded the design and implementation of an end-to-end Python pipeline to analyze key metrics.'")
            st.warning("👉 **Option 3 (Technical Focus):** 'Engineered a high-performance Python application utilizing optimized data structures for real-time analysis.'")

# ==================== TAB 4: SMART PLACEMENT & RED FLAGS ====================
with tab4:
    st.subheader("💡 ATS Keyword Placement & Red Flag Detector")
    if resume_text.strip() != "" and job_description.strip() != "":
        missing = get_missing_keywords(resume_text, job_description)
        st.markdown("### 📍 Where to Add Missing Keywords?")
        if missing:
            for i, kw in enumerate(missing[:6]):
                st.info(f"**Keyword:** `{kw.capitalize()}` ➔ **Suggested Bullet:** *'Successfully utilized {kw} in hands-on projects to improve workflow and optimization.'* (Add to **Skills/Projects** section)")

        st.divider()
        st.markdown("### 🚩 Resume Weakness & Cliché Detector")
        cliches = ['hardworking', 'honest', 'team player', 'self motivated', 'go getter', 'fast learner']
        found_cliches = [c for c in cliches if c in resume_text.lower()]
        if found_cliches:
            st.warning(f"⚠️ Found Overused Buzzwords: {', '.join(found_cliches)}")
        else:
            st.success("✅ Clean Resume! No weak buzzwords detected.")

# ==================== TAB 5: SALARY PREDICTOR ====================
with tab5:
    st.subheader("💰 Market Experience & Salary Range Predictor")
    if job_description.strip() != "":
        target_role = extract_job_title(job_description)
        exp_match = re.search(r'(\d+)\+?\s*(years|yrs)', job_description.lower())
        exp_years = int(exp_match.group(1)) if exp_match else 2
        base_pay = 4 + (exp_years * 2.5)
        st.metric("Predicted Annual Package (India Market)", f"₹{base_pay:.1f} LPA - ₹{base_pay + 5:.1f} LPA")

# ==================== TAB 6: HR COLD OUTREACH ====================
with tab6:
    st.subheader("✉️ HR Cold Email & LinkedIn Message Generator")
    if resume_text.strip() != "" and job_description.strip() != "":
        target_role = extract_job_title(job_description)
        st.code(f"Hi [Hiring Manager], I came across the {target_role} opening. I'd love to connect!", language="text")

# ==================== TAB 7: MOCK INTERVIEW ====================
with tab7:
    st.subheader("🎤 AI Technical Mock Interview Practice")
    if job_description.strip() != "":
        target_role = extract_job_title(job_description)
        st.write(f"Practice top interview questions for **{target_role}**")
