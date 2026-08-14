import math
import re
import urllib.parse
from collections import Counter
import streamlit as st
from PIL import Image

# ==================== Multi-level PDF & File Extraction Libraries ====================
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

# Streamlit Page Config
st.set_page_config(
    page_title="AI Resume Suite & Career Hub", page_icon="🚀", layout="wide"
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
    "🎤 AI Mock Interview",
])


# 4-Layer Bulletproof Text Extractor
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""

    file_type = uploaded_file.name.split(".")[-1].lower()
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
    words = re.findall(r"\w+", text.lower())
    return Counter(words)


def get_cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return float(numerator) / denominator if denominator else 0.0


def get_missing_keywords(resume_text, jd_text):
    clean_resume = set(re.findall(r"\b[a-zA-Z]{3,}\b", resume_text.lower()))
    clean_jd = set(re.findall(r"\b[a-zA-Z]{3,}\b", jd_text.lower()))
    stop_words = {
        "and",
        "the",
        "for",
        "with",
        "you",
        "this",
        "that",
        "from",
        "have",
        "will",
        "are",
        "your",
        "our",
        "work",
        "experience",
        "looking",
        "role",
        "team",
        "company",
        "required",
        "skills",
        "good",
        "must",
    }
    return list((clean_jd - stop_words) - (clean_resume - stop_words))[:12]


def extract_job_title(jd_text):
    lines = jd_text.strip().split("\n")
    for line in lines[:5]:
        if any(
            term in line.lower()
            for term in [
                "title",
                "role",
                "engineer",
                "analyst",
                "developer",
                "designer",
                "manager",
            ]
        ):
            return re.sub(r"[^a-zA-Z0-9\s]", "", line).strip()
    return "Software Developer"


def format_bullet_points(text):
    if not text.strip():
        return ""
    lines = text.strip().split("\n")
    html_out = ""
    in_list = False

    for line in lines:
        line_str = line.strip()
        if (
            line_str.startswith("- ")
            or line_str.startswith("* ")
            or line_str.startswith("• ")
        ):
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


def calculate_general_resume_score(text):
    score = 0
    feedback = []
    word_count = len(text.split())

    # 1. Word Count Check
    if 250 <= word_count <= 1000:
        score += 25
        feedback.append(
            "✅ **Ideal Length:** Resume length is optimal for ATS readable scans."
        )
    elif word_count < 250:
        score += 10
        feedback.append(
            "⚠️ **Too Short:** Resume might be lacking details. Aim for at least 300+ words."
        )
    else:
        score += 15
        feedback.append(
            "⚠️ **Too Long:** Try to condense your resume to 1-2 pages."
        )

    # 2. Key Sections Check
    text_lower = text.lower()
    sections = ["education", "skills", "experience", "projects"]
    found_sections = [s for s in sections if s in text_lower]
    score += len(found_sections) * 10
    feedback.append(
        f"✅ **Essential Sections Found:** Found {len(found_sections)}/4 key sections ({', '.join([s.capitalize() for s in found_sections])})."
    )

    # 3. Action Verbs Check
    action_words = [
        "developed",
        "managed",
        "created",
        "built",
        "designed",
        "implemented",
        "led",
        "improved",
        "analyzed",
        "engineered",
    ]
    found_verbs = [v for v in action_words if v in text_lower]
    if len(found_verbs) >= 4:
        score += 20
        feedback.append(
            f"✅ **Strong Action Verbs:** Good usage of power words like `{', '.join(found_verbs[:4])}`."
        )
    else:
        score += 10
        feedback.append(
            "💡 **Action Verbs:** Consider adding more action words (e.g., *Built, Engineered, Developed*)."
        )

    # 4. Contact Details Check
    if any(k in text_lower for k in ["email", "@", "linkedin", "github", "phone"]):
        score += 15
        feedback.append(
            "✅ **Contact Information:** Contact or portfolio details detected."
        )
    else:
        feedback.append(
            "⚠️ **Contact Info Missing:** Ensure your email or phone number is clearly stated."
        )

    return score, feedback


# ==================== Sidebar Setup ====================
st.sidebar.header("📥 Upload Documents")
resume_file = st.sidebar.file_uploader(
    "Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"]
)
resume_text_input = st.sidebar.text_area(
    "OR Paste Resume Text",
    value=st.session_state["built_resume_text"],
    height=150,
)

extracted_resume = extract_text_from_file(resume_file)
resume_text = extracted_resume if extracted_resume != "" else resume_text_input

if resume_file:
    if extracted_resume != "":
        st.sidebar.success(
            f"✅ Loaded {len(extracted_resume.split())} words from Resume!"
        )
    else:
        st.sidebar.warning(
            "⚠️ Could not extract text. Please paste text in box below."
        )

st.sidebar.divider()

has_jd = st.sidebar.radio(
    "Do you have a Job Description (JD) to match?",
    ["No (Check General Resume Score)", "Yes (Compare with Job Description)"],
)

job_description = ""
if has_jd == "Yes (Compare with Job Description)":
    jd_file = st.sidebar.file_uploader(
        "Upload Job Description (.txt, .pdf, .docx)",
        type=["pdf", "docx", "txt"],
    )
    jd_text_input = st.sidebar.text_area("OR Paste JD Text", height=150)

    extracted_jd = extract_text_from_file(jd_file)
    job_description = extracted_jd if extracted_jd != "" else jd_text_input

    if jd_file and extracted_jd != "":
        st.sidebar.success(
            f"✅ Loaded {len(extracted_jd.split())} words from JD!"
        )


# ==================== TAB 1: RESUME ANALYZER & JOBS ====================
with tab1:
    st.subheader("📊 Resume Score & Analysis")

    if st.button("Run Full Analysis 🚀", type="primary"):
        if resume_text.strip() == "":
            st.error("Please upload or paste your Resume first in the Sidebar!")
        else:
            if (
                has_jd == "Yes (Compare with Job Description)"
                and job_description.strip() != ""
            ):
                v1 = text_to_vector(resume_text)
                v2 = text_to_vector(job_description)
                match_percentage = round(
                    get_cosine_similarity(v1, v2) * 100, 2
                )
                missing_skills = get_missing_keywords(
                    resume_text, job_description
                )
                target_role = extract_job_title(job_description)
                encoded_role = urllib.parse.quote(target_role)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="🎯 Job Match Score", value=f"{match_percentage}%"
                    )
                    if match_percentage >= 50:
                        st.success(
                            "🎯 High Match Alignment with Job Description!"
                        )
                    elif match_percentage >= 25:
                        st.warning(
                            "⚠️ Moderate Alignment. Needs improvement."
                        )
                    else:
                        st.error(
                            "❌ Low Alignment. Add relevant missing keywords."
                        )
                with col2:
                    st.write("**Missing Keywords from JD:**")
                    st.write(
                        ", ".join([f"`{w}`" for w in missing_skills])
                        if missing_skills
                        else "None! Excellent Job."
                    )

                st.divider()
                st.subheader(f"💼 Live Job Openings: {target_role}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.link_button(
                        "Apply on LinkedIn 🚀",
                        f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}",
                        use_container_width=True,
                    )
                with c2:
                    st.link_button(
                        "Apply on Naukri 🚀",
                        f"https://www.naukri.com/{encoded_role.replace('%20', '-')}-jobs",
                        use_container_width=True,
                    )
                with c3:
                    st.link_button(
                        "Apply on Indeed 🚀",
                        f"https://www.indeed.com/jobs?q={encoded_role}",
                        use_container_width=True,
                    )

            else:
                gen_score, feedback_list = calculate_general_resume_score(
                    resume_text
                )

                st.metric(
                    label="📈 General Resume Quality Score",
                    value=f"{gen_score} / 100",
                )

                if gen_score >= 75:
                    st.success(
                        "🌟 Excellent Resume Structure & ATS Readiness!"
                    )
                elif gen_score >= 50:
                    st.warning("⚠️ Good Resume, but can be improved further.")
                else:
                    st.error(
                        "❌ Low Score. Consider adding missing sections or content."
                    )

                st.divider()
                st.markdown("### 🔍 ATS Quality Feedback Summary:")
                for item in feedback_list:
                    st.write(item)


# ==================== TAB 2: LIVE RESUME EDITOR & BUILDER ====================
with tab2:
    st.subheader("✏️ Resume Upload & Interactive Editor")
    st.write(
        "Upload your resume to automatically extract and populate details into the fields below for quick editing."
    )

    # Session State Keys Initialization
    keys = [
        "ed_name",
        "ed_title",
        "ed_email",
        "ed_phone",
        "ed_loc",
        "ed_obj",
        "ed_skills",
        "ed_exp",
        "ed_proj",
        "ed_edu",
        "ed_cert",
    ]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = ""

    uploaded_edit_file = st.file_uploader(
        "📂 Upload Resume to Edit (.pdf, .docx, .txt)",
        type=["pdf", "docx", "txt"],
        key="editor_file",
    )

    if uploaded_edit_file is not None:
        if st.button(
            "📥 Parse & Load Resume into Editor Boxes", type="primary"
        ):
            extracted_raw = extract_text_from_file(uploaded_edit_file)
            if extracted_raw:
                lines = [
                    line.strip()
                    for line in extracted_raw.split("\n")
                    if line.strip()
                ]

                # Basic Info Extraction
                if lines:
                    st.session_state["ed_name"] = lines[0]
                if len(lines) > 1 and not re.search(
                    r"@|http|\d{5}", lines[1]
                ):
                    st.session_state["ed_title"] = lines[1]

                emails = re.findall(
                    r"[\w\.-]+@[\w\.-]+\.\w+", extracted_raw
                )
                if emails:
                    st.session_state["ed_email"] = emails[0]

                phones = re.findall(
                    r"[\+\(]?[0-9][0-9\-\s\(\)]{8,}[0-9]", extracted_raw
                )
                if phones:
                    st.session_state["ed_phone"] = phones[0]

                # Section Parser Helper
                def get_section_text(text, keywords):
                    text_lines = text.split("\n")
                    capturing = False
                    result = []
                    all_headings = [
                        "education",
                        "skills",
                        "experience",
                        "projects",
                        "certifications",
                        "summary",
                        "objective",
                        "work history",
                    ]
                    for line in text_lines:
                        l_str = line.strip().lower()
                        if any(k in l_str for k in keywords) and len(l_str) < 35:
                            capturing = True
                            continue
                        elif capturing and any(
                            h in l_str
                            for h in all_headings
                            if not any(k in h for k in keywords)
                        ) and len(l_str) < 35:
                            break
                        if capturing:
                            result.append(line)
                    return "\n".join(result).strip()

                st.session_state["ed_obj"] = get_section_text(
                    extracted_raw, ["objective", "summary", "profile"]
                )
                st.session_state["ed_skills"] = get_section_text(
                    extracted_raw,
                    ["skills", "technical skills", "technologies"],
                )
                st.session_state["ed_exp"] = get_section_text(
                    extracted_raw, ["experience", "work history", "employment"]
                )
                st.session_state["ed_proj"] = get_section_text(
                    extracted_raw, ["projects", "personal projects"]
                )
                st.session_state["ed_edu"] = get_section_text(
                    extracted_raw, ["education", "academic", "qualifications"]
                )
                st.session_state["ed_cert"] = get_section_text(
                    extracted_raw, ["certifications", "licenses", "certificates"]
                )

                st.success(
                    "✅ Content parsed successfully into form fields below!"
                )

    st.divider()

    # Form Fields
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["ed_name"] = st.text_input(
            "Full Name", value=st.session_state["ed_name"]
        )
        st.session_state["ed_email"] = st.text_input(
            "Email Address", value=st.session_state["ed_email"]
        )
        st.session_state["ed_loc"] = st.text_input(
            "Location (City, Country)", value=st.session_state["ed_loc"]
        )
    with c2:
        st.session_state["ed_title"] = st.text_input(
            "Target Title", value=st.session_state["ed_title"]
        )
        st.session_state["ed_phone"] = st.text_input(
            "Phone Number", value=st.session_state["ed_phone"]
        )

    st.session_state["ed_obj"] = st.text_area(
        "Professional Summary / Objective",
        value=st.session_state["ed_obj"],
        height=90,
    )
    st.session_state["ed_skills"] = st.text_area(
        "Technical Skills (Comma separated or line items)",
        value=st.session_state["ed_skills"],
        height=90,
    )
    st.session_state["ed_exp"] = st.text_area(
        "Work Experience (Use - or * for bullet points)",
        value=st.session_state["ed_exp"],
        height=140,
    )
    st.session_state["ed_proj"] = st.text_area(
        "Key Projects", value=st.session_state["ed_proj"], height=120
    )
    st.session_state["ed_edu"] = st.text_area(
        "Education Details", value=st.session_state["ed_edu"], height=90
    )
    st.session_state["ed_cert"] = st.text_area(
        "Certifications & Achievements",
        value=st.session_state["ed_cert"],
        height=80,
    )

    # Generate Full Compiled Text
    built_resume = f"""{st.session_state['ed_name'].upper()}
{st.session_state['ed_title']}
Email: {st.session_state['ed_email']} | Phone: {st.session_state['ed_phone']} | Location: {st.session_state['ed_loc']}

SUMMARY
{st.session_state['ed_obj']}

TECHNICAL SKILLS
{st.session_state['ed_skills']}

WORK EXPERIENCE
{st.session_state['ed_exp']}

PROJECTS
{st.session_state['ed_proj']}

EDUCATION
{st.session_state['ed_edu']}

CERTIFICATIONS
{st.session_state['ed_cert']}
"""
    st.session_state["built_resume_text"] = built_resume.strip()

    st.subheader("📄 Live Formatted Resume Preview")
    html_preview = f"""
    <div style="background-color: #ffffff; color: #333333; padding: 25px; border-radius: 8px; border: 1px solid #ddd; font-family: Arial, sans-serif;">
        <h2 style="margin: 0; color: #1a365d; font-size: 24px;">{st.session_state['ed_name']}</h2>
        <p style="margin: 2px 0 8px 0; font-weight: bold; color: #2b6cb0; font-size: 14px;">{st.session_state['ed_title']}</p>
        <p style="margin-bottom: 12px; font-size: 12px; color: #666;">
            {st.session_state['ed_email']} | {st.session_state['ed_phone']} | {st.session_state['ed_loc']}
        </p>
        <hr style="border: 0.5px solid #ccc; margin-bottom: 12px;"/>
        
        <h4 style="color: #2b6cb0; margin-bottom: 4px; font-size: 14px;">SUMMARY</h4>
        <p style="font-size: 12.5px;">{st.session_state['ed_obj']}</p>
        
        <h4 style="color: #2b6cb0; margin-bottom: 4px; font-size: 14px;">SKILLS</h4>
        <p style="font-size: 12.5px;">{st.session_state['ed_skills']}</p>
        
        <h4 style="color: #2b6cb0; margin-bottom: 4px; font-size: 14px;">EXPERIENCE</h4>
        {format_bullet_points(st.session_state['ed_exp'])}
        
        <h4 style="color: #2b6cb0; margin-bottom: 4px; font-size: 14px;">PROJECTS</h4>
        {format_bullet_points(st.session_state['ed_proj'])}
        
        <h4 style="color: #2b6cb0; margin-bottom: 4px; font-size: 14px;">EDUCATION</h4>
        <p style="font-size: 12.5px;">{st.session_state['ed_edu']}</p>
    </div>
    """
    st.markdown(html_preview, unsafe_allow_html=True)

    st.download_button(
        label="📥 Download Resume as Text File",
        data=st.session_state["built_resume_text"],
        file_name="Updated_Resume.txt",
        mime="text/plain",
    )


# ==================== TAB 3: AI BULLET REWRITER ====================
with tab3:
    st.subheader("✨ Bullet Point Enhancement Studio")
    st.write(
        "Transform basic job bullets into impact-driven, metric-rich statements."
    )

    bullet_input = st.text_input(
        "Enter a bullet point to enhance:",
        value="Responsible for managing database and improving code.",
    )

    if st.button("Enhance Bullet Point 🚀"):
        if bullet_input:
            st.markdown("### 💡 Recommended Bullet Variations:")
            st.success(
                f"**1. Action & Metric-Oriented:** Optimized relational database queries and refactored core codebase, driving a **35% reduction** in response times."
            )
            st.info(
                f"**2. Leadership Focus:** Spearheaded database management initiatives and standardized code architecture across cross-functional teams."
            )
            st.warning(
                f"**3. Technical Precision:** Architected high-performance database schema and implemented rigorous code review guidelines to minimize tech debt."
            )


# ==================== TAB 4: KEYWORD PLACEMENT & RED FLAGS ====================
with tab4:
    st.subheader("🎯 Keyword Placement & Formatting Audit")

    if resume_text.strip() == "":
        st.info("Upload or paste a resume in the sidebar to review audit logs.")
    else:
        st.markdown("### 🚦 Resume Health Checks:")

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("#### 🚩 Formatting & Layout")
            if len(resume_text.split()) < 200:
                st.error("❌ Word count low (Under 200 words).")
            else:
                st.success("✅ Content density is solid.")

            if "@" in resume_text:
                st.success("✅ Email address detected.")
            else:
                st.error("❌ Missing email contact.")

        with col_b:
            st.write("#### 🔑 Section Coverage")
            for sec in ["Skills", "Experience", "Education", "Projects"]:
                if sec.lower() in resume_text.lower():
                    st.success(f"✅ Heading `{sec}` found.")
                else:
                    st.warning(f"⚠️ Heading `{sec}` missing or unparsed.")


# ==================== TAB 5: SALARY PREDICTOR ====================
with tab5:
    st.subheader("💰 Salary Estimation Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        role = st.selectbox(
            "Select Target Role",
            [
                "Software Engineer",
                "Data Analyst",
                "Data Scientist",
                "DevOps Engineer",
                "Product Manager",
            ],
        )
    with c2:
        exp = st.slider("Years of Experience", 0, 15, 3)
    with c3:
        loc = st.selectbox(
            "Select Region", ["India (LPA)", "United States ($)", "Europe (€)"]
        )

    base_rates = {
        "Software Engineer": {"India (LPA)": 6, "United States ($)": 80000, "Europe (€)": 50000},
        "Data Analyst": {"India (LPA)": 5, "United States ($)": 65000, "Europe (€)": 42000},
        "Data Scientist": {"India (LPA)": 8, "United States ($)": 95000, "Europe (€)": 58000},
        "DevOps Engineer": {"India (LPA)": 7, "United States ($)": 90000, "Europe (€)": 55000},
        "Product Manager": {"India (LPA)": 10, "United States ($)": 105000, "Europe (€)": 65000},
    }

    base = base_rates[role][loc]
    multiplier = 1 + (exp * 0.15)
    estimated_val = round(base * multiplier, 1)

    unit = "LPA" if "India" in loc else ("$" if "United" in loc else "€")
    st.metric(
        label=f"Estimated Compensation Range ({loc})",
        value=f"{unit} {estimated_val} - {round(estimated_val * 1.25, 1)} {unit}",
    )


# ==================== TAB 6: HR COLD OUTREACH ====================
with tab6:
    st.subheader("✉️ HR Cold Outreach Email & Message Generator")

    c1, c2 = st.columns(2)
    with c1:
        rec_name = st.text_input("Recruiter / Manager Name", "Hiring Manager")
        comp_name = st.text_input("Company Name", "Target Company")
    with c2:
        outreach_role = st.text_input("Job Role", "Software Engineer")
        platform = st.selectbox(
            "Channel", ["LinkedIn Message", "Email Template"]
        )

    if st.button("Generate Outreach Message ✉️"):
        if platform == "LinkedIn Message":
            msg = f"Hi {rec_name}, I came across the {outreach_role} opening at {comp_name} and wanted to reach out. With my background in building scalable software systems, I’d love to explore how I can contribute to your team. Thanks!"
        else:
            msg = f"""Subject: Application for {outreach_role} - {st.session_state.get('ed_name', 'Applicant')}

Dear {rec_name},

I hope this email finds you well.

I am writing to express my strong interest in the {outreach_role} position at {comp_name}. Having closely followed your team's work, I am eager to apply my experience in software development to contribute to your goals.

I have attached my resume for your review and would welcome the opportunity to connect.

Best regards,
{st.session_state.get('ed_name', 'Your Name')}"""

        st.code(msg, language="text")


# ==================== TAB 7: AI MOCK INTERVIEW ====================
with tab7:
    st.subheader("🎤 AI Mock Interview Practice")

    target_interview_role = st.text_input(
        "Target Role for Interview:", "Software Engineer"
    )

    if st.button("Generate Interview Questions 🎯"):
        st.markdown(f"### Mock Questions for {target_interview_role}:")
        st.write(
            "**1. Technical:** Describe a complex technical challenge you faced in your past project and how you solved it."
        )
        st.write(
            "**2. Behavioral:** How do you prioritize tasks when working under strict deadlines with shifting requirements?"
        )
        st.write(
            "**3. System/Architecture:** What steps do you take to ensure scalability and maintainability when writing code?"
        )

    user_ans = st.text_area("Type your response to practice:")
    if st.button("Submit Answer for Feedback"):
        if user_ans.strip():
            st.success(
                "✅ Good structure! Try structuring your response using the **STAR method** (Situation, Task, Action, Result) for maximum impact."
            )
        else:
            st.warning("Please type your response before submitting.")
