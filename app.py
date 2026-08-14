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
    st.write("మీ రెజ్యూమ్‌ని అప్‌లోడ్ చేసి బటన్ నొక్కగానే, వివరాలన్నీ కింద ఉన్న బాక్సులలోకి ఆటోమేటిక్‌గా లోడ్ అవుతాయి. అక్కడ మీరు సులభంగా మోడిఫై చేసుకోవచ్చు.")
    
    # Session State Initialization for Smart Auto-Fill
    if "ed_name" not in st.session_state: st.session_state["ed_name"] = ""
    if "ed_title" not in st.session_state: st.session_state["ed_title"] = ""
    if "ed_email" not in st.session_state: st.session_state["ed_email"] = ""
    if "ed_phone" not in st.session_state: st.session_state["ed_phone"] = ""
    if "ed_loc" not in st.session_state: st.session_state["ed_loc"] = ""
    if "ed_obj" not in st.session_state: st.session_state["ed_obj"] = ""
    if "ed_skills" not in st.session_state: st.session_state["ed_skills"] = ""
    if "ed_exp" not in st.session_state: st.session_state["ed_exp"] = ""
    if "ed_proj" not in st.session_state: st.session_state["ed_proj"] = ""
    if "ed_edu" not in st.session_state: st.session_state["ed_edu"] = ""
    if "ed_cert" not in st.session_state: st.session_state["ed_cert"] = ""

    # 1. File Upload Section
    uploaded_edit_file = st.file_uploader("📂 Upload Resume to Edit (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="editor_file")
    
    if uploaded_edit_file is not None:
        if st.button("📥 Parse & Load Resume into Editor Boxes", type="primary"):
            extracted_raw = extract_text_from_file(uploaded_edit_file)
            if extracted_raw:
                lines = [line.strip() for line in extracted_raw.split('\n') if line.strip()]
                
                # Simple Smart Parsing Logic
                # Name (Usually first non-empty line)
                if lines:
                    st.session_state["ed_name"] = lines[0]
                
                # Email Extraction Regex/Check
                import re
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', extracted_raw)
                if emails: st.session_state["ed_email"] = emails[0]
                
                # Phone Number Extraction Regex/Check
                phones = re.findall(r'[\+\(]?[0-9][0-9\-\s\(\)]{8,}[0-9]', extracted_raw)
                if phones: st.session_state["ed_phone"] = phones[0]

                # Section Extraction Logic based on Headings
                lower_text = extracted_raw.lower()
                
                # Helper to split text by headers
                def get_section_text(text, keywords):
                    text_lines = text.split('\n')
                    capturing = False
                    result = []
                    for line in text_lines:
                        l_str = line.strip().lower()
                        # If line matches section heading
                        if any(k in l_str for k in keywords) and len(l_str) < 35:
                            capturing = True
                            continue
                        # If hit another potential heading stop
                        elif capturing and any(h in l_str for h in ['education', 'skills', 'experience', 'projects', 'certifications', 'summary', 'objective']) and len(l_str) < 35:
                            break
                        if capturing:
                            result.append(line)
                    return '\n'.join(result).strip()

                parsed_obj = get_section_text(extracted_raw, ['objective', 'summary', 'profile'])
                parsed_skills = get_section_text(extracted_raw, ['skills', 'technical skills', 'technologies'])
                parsed_exp = get_section_text(extracted_raw, ['experience', 'work experience', 'employment', 'internship'])
                parsed_proj = get_section_text(extracted_raw, ['projects', 'academic projects'])
                parsed_edu = get_section_text(extracted_raw, ['education', 'qualification', 'academic background'])
                parsed_cert = get_section_text(extracted_raw, ['certifications', 'certificates'])

                if parsed_obj: st.session_state["ed_obj"] = parsed_obj
                if parsed_skills: st.session_state["ed_skills"] = parsed_skills
                if parsed_exp: st.session_state["ed_exp"] = parsed_exp
                else: st.session_state["ed_exp"] = extracted_raw  # Fallback to full raw text if sections fail
                if parsed_proj: st.session_state["ed_proj"] = parsed_proj
                if parsed_edu: st.session_state["ed_edu"] = parsed_edu
                if parsed_cert: st.session_state["ed_cert"] = parsed_cert

                st.success("✅ Resume details loaded & filled into editor boxes! You can edit them below.")
            else:
                st.error("Could not extract text from this file. Please make sure it's a readable PDF or DOCX file.")

    st.divider()

    theme_choice = st.radio("🎨 Choose Resume Theme:", ["Modern Blue", "Executive Gold/Black", "Minimal Dark Header"], horizontal=True)

    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("### 📝 Edit Resume Sections")
        
        # Text Inputs with Auto-Filled Values from Uploaded File
        full_name = st.text_input("Full Name", value=st.session_state["ed_name"], placeholder="e.g., John Doe")
        title = st.text_input("Professional Title", value=st.session_state["ed_title"], placeholder="e.g., Software Engineer")
        email = st.text_input("Email", value=st.session_state["ed_email"], placeholder="e.g., johndoe@example.com")
        phone = st.text_input("Phone Number", value=st.session_state["ed_phone"], placeholder="e.g., +91 9876543210")
        location = st.text_input("Location", value=st.session_state["ed_loc"], placeholder="e.g., Hyderabad, India")
        linkedin = st.text_input("LinkedIn Profile URL", value="", placeholder="https://www.linkedin.com/in/yourprofile")
        github = st.text_input("GitHub Profile URL", value="", placeholder="https://github.com/yourusername")

        st.markdown("---")
        objective = st.text_area("Edit Objective / Summary", value=st.session_state["ed_obj"], placeholder="Career objective or summary...", height=90)
        skills = st.text_area("Edit Skills", value=st.session_state["ed_skills"], placeholder="- Python, SQL, Streamlit...", height=110)
        experience = st.text_area("Edit Work / Internship Experience", value=st.session_state["ed_exp"], placeholder="Work experience details...", height=150)
        projects = st.text_area("Edit Projects", value=st.session_state["ed_proj"], placeholder="Project details...", height=120)
        education = st.text_area("Edit Education", value=st.session_state["ed_edu"], placeholder="Degree | College Name...", height=100)
        certifications = st.text_area("Edit Certifications (Optional)", value=st.session_state["ed_cert"], placeholder="Certifications...", height=80)
        languages = st.text_area("Languages Spoken", value="- English\n- Telugu", height=70)
        declaration = st.text_area("Declaration Statement", value="I hereby declare that all information provided is accurate to the best of my knowledge.", height=70)
        dec_date = st.text_input("Date", value="", placeholder="DD/MM/YYYY")

        # Fallbacks for live preview display
        p_name = full_name if full_name.strip() else "Your Full Name"
        p_title = title if title.strip() else "Professional Title"
        p_email = email if email.strip() else "email@example.com"
        p_phone = phone if phone.strip() else "+91 9876543210"
        p_loc = location if location.strip() else "City, Country"

        # Sync edited content with Tab 1 (Analyzer)
        edited_full_text = f"{p_name}\n{p_title}\n{objective}\n{skills}\n{experience}\n{projects}\n{education}\n{certifications}"
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

        linkedin_url = format_url(linkedin) if linkedin.strip() else ""
        github_url = format_url(github) if github.strip() else ""

        contact_items = [f"📍 {p_loc}", f"📞 {p_phone}", f"📧 {p_email}"]
        if linkedin_url:
            contact_items.append(f"<a href='{linkedin_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{linkedin.strip()}</a>")
        if github_url:
            contact_items.append(f"<a href='{github_url}' target='_blank' style='color:{primary_color}; text-decoration: underline;'>{github.strip()}</a>")
        
        contact_html = " &nbsp;|&nbsp; ".join(contact_items)

        obj_s = f"<h3 style='color:{primary_color};'>Career Objective</h3>{format_bullet_points(objective)}" if objective.strip() else ""
        edu_s = f"<h3 style='color:{primary_color};'>Education</h3>{format_bullet_points(education)}" if education.strip() else ""
        skl_s = f"<h3 style='color:{primary_color};'>Technical Skills</h3>{format_bullet_points(skills)}" if skills.strip() else ""
        crt_s = f"<h3 style='color:{primary_color};'>Certifications</h3>{format_bullet_points(certifications)}" if certifications.strip() else ""
        prj_s = f"<h3 style='color:{primary_color};'>Projects</h3>{format_bullet_points(projects)}" if projects.strip() else ""
        exp_s = f"<h3 style='color:{primary_color};'>Experience / Internship</h3>{format_bullet_points(experience)}" if experience.strip() else ""
        lng_s = f"<h3 style='color:{primary_color};'>Languages Spoken</h3>{format_bullet_points(languages)}" if languages.strip() else ""
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
                    <h1>{p_name}</h1>
                    <div class="title">{p_title}</div>
                    <div class="contact">{contact_html}</div>
                </div>
                <hr>
                
                {obj_s} {skl_s} {exp_s} {prj_s} {edu_s} {crt_s} {lng_s} {dec_s}
                
                <table class="footer-table">
                    <tr>
                        <td><strong>Location:</strong> {p_loc}</td>
                        <td style="text-align: right;"><strong>Signature:</strong> {p_name}</td>
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
            file_name=f"{p_name.replace(' ', '_')}_Resume.html",
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
    st.subheader("✉️ HR Cold Outreach & Referral Generator")
    st.write("మీ రెజ్యూమ్ వివరాల ఆధారంగా HR లేదా రిక్రూటర్ల కోసం ప్రొఫెషనల్ ఈమెయిళ్ళు మరియు లింక్డ్ఇన్ మెసేజ్లు ఇక్కడ జనరేట్ అవుతాయి.")

    # Get candidate details from active session or input
    candidate_name = p_name if 'p_name' in locals() and p_name != "Your Full Name" else "Candidate"
    candidate_skills = skills if 'skills' in locals() and skills.strip() else "Software Development, Problem Solving"
    
    st.markdown("### 🎯 Outreach Options")
    target_company = st.text_input("Enter Target Company Name", placeholder="e.g., TCS, Google, Infosys")
    job_role = st.text_input("Enter Job Role You're Applying For", placeholder="e.g., Software Engineer, Data Analyst")

    if st.button("🚀 Generate Outreach Messages", type="primary"):
        if not target_company or not job_role:
            st.warning("Please enter both Target Company Name and Job Role above!")
        else:
            comp_name = target_company.strip()
            role_name = job_role.strip()

            st.divider()
            
            # 1. Cold Email Template
            st.markdown("### 📧 1. Personalized HR Cold Email")
            email_subject = f"Application for {role_name} Position - {candidate_name}"
            email_body = f"""Dear Hiring Team at {comp_name},

I hope this email finds you well.

I am reaching out to express my strong interest in the {role_name} position at {comp_name}. With my background in {candidate_skills[:80]}..., I am confident in my ability to add immediate value to your engineering team.

Key highlights from my experience:
- Hands-on expertise in key industry domains and modern tech stack.
- Proven track record of delivering clean code and working on end-to-end projects.

I have attached my resume for your review. I would welcome the opportunity to discuss how my skill set aligns with the goals of {comp_name}.

Thank you for your time and consideration.

Best regards,
{candidate_name}
"""
            st.code(f"Subject: {email_subject}\n\n{email_body}", language="text")

            # 2. LinkedIn Connection Note
            st.markdown("### 💼 2. LinkedIn Recruiter Message (Under 300 Chars)")
            linkedin_msg = f"Hi, I noticed active engineering roles at {comp_name}. As a {role_name} skilled in {candidate_skills[:40]}..., I’d love to connect and learn more about opportunities on your team. Thanks! - {candidate_name}"
            st.code(linkedin_msg, language="text")

            # 3. Elevator Pitch (30 Sec Intro)
            st.markdown("### 🎙️ 3. Elevator Pitch (For HR Calls)")
            pitch = f"Hi, I'm {candidate_name}. I specialize in {candidate_skills[:60]}... I recently built projects focusing on core domain solutions, and I am actively looking for a {role_name} role at {comp_name} where I can deliver impactful results."
            st.info(f"**Your Pitch:** {pitch}")


# ==================== TAB 7: AI MOCK INTERVIEW ====================
with tab7:
    st.subheader("🎤 AI Mock Interview Assistant")
    st.write("మీ రెజ్యూమ్ ప్రాజెక్టులు మరియు స్కిల్స్ ఆధారంగా అడిగే అవకాశం ఉన్న మోస్ట్ ఇంపార్టెంట్ ఇంటర్వ్యూ ప్రశ్నలు ఇక్కడ ఉన్నాయి.")

    # Determine Active Resume Text
    active_resume_text = resume_text if 'resume_text' in locals() and resume_text.strip() else edited_full_text if 'edited_full_text' in locals() else ""

    if st.button("🎯 Generate Interview Questions from My Resume", type="primary"):
        if not active_resume_text.strip():
            st.error("Please upload or edit a resume first to generate questions!")
        else:
            st.success("✅ Custom Interview Questions Generated based on your Resume details!")
            
            st.divider()
            
            st.markdown("### 💬 1. HR & Behavioral Questions")
            st.markdown("""
            * **Q1: Tell me about yourself and your background based on your resume.**
              > *Tip:* Focus on your skills, 1-2 major projects, and why you are suitable for this role.
            * **Q2: Why do you want to join our company?**
              > *Tip:* Mention company achievements, mission, and how your career goals align with them.
            * **Q3: Describe a challenge you faced during a project and how you solved it.**
              > *Tip:* Use the **STAR Method** (Situation, Task, Action, Result).
            """)

            st.markdown("---")
            
            st.markdown("### 🛠️ 2. Domain & Resume Specific Technical Questions")
            
            # Simple keyword matching to render relevant tech questions
            res_lower = active_resume_text.lower()
            
            q_count = 1
            if "python" in res_lower:
                st.markdown(f"**Q{q_count}: What are lists and tuples in Python? How do you manage memory management in Python?**")
                q_count += 1
            if "sql" in res_lower or "database" in res_lower:
                st.markdown(f"**Q{q_count}: What is the difference between WHERE and HAVING clause in SQL? Explain Joins.**")
                q_count += 1
            if "project" in res_lower:
                st.markdown(f"**Q{q_count}: Explain the architecture and technical challenges of your primary project mentioned in the resume.**")
                q_count += 1
            if "javascript" in res_lower or "react" in res_lower or "web" in res_lower:
                st.markdown(f"**Q{q_count}: Explain state vs props in React or asynchronous programming in JS.**")
                q_count += 1
            
            # Fallback general technical question
            st.markdown(f"**Q{q_count}: How do you test and debug your code before submitting a project?**")

            st.divider()
            st.markdown("### ✍️ Practice Your Answer")
            user_ans = st.text_area("Type your answer here to practice:", placeholder="Write your response here...")
            if st.button("Submit Answer for Review"):
                if len(user_ans.split()) > 20:
                    st.success("👍 Good response! You explained with sufficient details. Make sure to keep your tone clear and confident during the live call.")
                else:
                    st.warning("⚠️ Your response seems a bit brief. Try adding specific examples or technical details using the STAR method.")
