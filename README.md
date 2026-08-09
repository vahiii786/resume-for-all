# 🚀 Smart AI Resume Hub & All-in-One Career Suite

An interactive **Streamlit-based AI Resume & Career Suite** designed to help job seekers analyze resumes, optimize them for ATS systems, create professional resumes, improve resume bullet points, estimate salary ranges, generate HR outreach messages, and practice mock interviews.

The application combines multiple career tools into a single, easy-to-use dashboard.

---

## ✨ Features

### 📊 1. Resume Analyzer & Job Matcher

* Upload or paste your resume.
* Upload or paste a Job Description (JD).
* Calculates a **resume-to-job match score** using cosine similarity.
* Identifies potentially missing keywords from the JD.
* Extracts the target job role.
* Provides quick links to search for jobs on:

  * LinkedIn
  * Naukri
  * Indeed

### ✏️ 2. Live Resume Builder

Create and preview a resume directly inside the application.

#### Supported sections:

* Full Name
* Professional Title
* Contact Information
* Location
* LinkedIn
* GitHub
* Career Objective
* Education
* Technical Skills
* Certifications
* Projects
* Work/Internship Experience
* Languages
* Interests/Hobbies
* Declaration

#### Resume themes:

* 🔵 Modern Blue
* 🟡 Executive Gold/Black
* ⚫ Minimal Dark Header

The generated resume can be downloaded as an **HTML file**, which can then be opened in a browser and printed/saved as PDF.

---

### ✨ 3. AI Bullet Rewriter

Convert basic resume statements into stronger, action-oriented bullet points.

For example:

> I made a Python app for analysis.

The application provides different improvement styles such as:

* 📈 Metric-focused
* ⚡ Action-focused
* 💻 Technical-focused

---

### 🎯 4. ATS Keyword Placement & Red Flag Detector

Helps identify areas where your resume could be improved.

#### Keyword analysis

* Finds potentially missing keywords from the Job Description.
* Suggests adding keywords to the **Skills** or **Projects** section.
* Generates sample bullet-point wording.

#### Red flag detection

Detects common resume clichés such as:

* Hardworking
* Honest
* Team player
* Self motivated
* Go getter
* Fast learner

It also suggests stronger action-oriented alternatives such as:

`Spearheaded` · `Engineered` · `Optimized` · `Implemented`

---

### 💰 5. Salary Predictor

Provides an estimated salary range based on the experience requirement detected in the Job Description.

The current prototype uses a simple rule-based calculation to estimate an annual package in **Indian LPA (Lakhs Per Annum)**.

> ⚠️ This is an approximate prototype and should not be treated as an actual market salary prediction.

---

### ✉️ 6. HR Cold Outreach Generator

Generates ready-to-use outreach content based on the target role.

#### Includes:

* LinkedIn connection request
* HR cold email
* Target job title automatically extracted from the Job Description

---

### 🎤 7. AI Mock Interview

Provides basic interview practice tailored to the target job role.

The current version includes questions such as:

* How have you applied your technical skills in previous projects?
* Describe a challenging bug you resolved recently.

Users can submit answers and receive basic improvement feedback.

---

## 🛠️ Tech Stack

| Technology          | Purpose                       |
| ------------------- | ----------------------------- |
| Python              | Core programming language     |
| Streamlit           | Web application framework     |
| PyPDF / PyPDF2      | PDF text extraction           |
| python-docx         | DOCX document extraction      |
| Regex               | Text and keyword processing   |
| Collections.Counter | Word-frequency vectors        |
| Math                | Cosine similarity calculation |
| urllib.parse        | Job-search URL generation     |
| HTML/CSS            | Resume preview and styling    |

---

## 📁 Project Structure

A simple project structure can look like this:

```text
smart-ai-resume-hub/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/smart-ai-resume-hub.git
cd smart-ai-resume-hub
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, create one containing:

```text
streamlit
pypdf
PyPDF2
python-docx
```

---

## ▶️ Run the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, typically:

```text
http://localhost:8501
```

Open that URL in your browser.

---

## 📄 Supported File Formats

### Resume

The application supports:

* `.pdf`
* `.docx`
* `.txt`

### Job Description

The application supports:

* `.pdf`
* `.docx`
* `.txt`

You can also paste resume and Job Description text directly into the sidebar.

---

## 🔍 How Resume Matching Works

The Resume Analyzer currently uses **word-frequency vectors and cosine similarity**.

Conceptually:

```text
Resume → Word Frequency Vector
             ↓
        Cosine Similarity
             ↓
Job Description → Word Frequency Vector
             ↓
       Match Percentage
```

The similarity score is converted into a percentage:

```text
Cosine Similarity × 100
```

The application also compares words found in the Job Description against words found in the resume to identify potentially missing keywords.

> Note: This is a lightweight text-matching approach rather than a production-grade semantic ATS model.

---

## 🎨 Resume Builder

The resume builder dynamically generates an HTML resume based on the information entered by the user.

The generated HTML includes:

* Custom colors
* Typography
* Section headings
* Bullet points
* Clickable LinkedIn/GitHub links
* Contact information
* Declaration
* Signature/date section

The HTML file can be downloaded and opened in a browser.

### Convert to PDF

1. Download the generated HTML resume.
2. Open it in Chrome/Edge/Firefox.
3. Press `Ctrl + P` on Windows/Linux or `Cmd + P` on macOS.
4. Select **Save as PDF**.

---

## 🧠 Current AI/Automation Approach

Despite the application's AI-focused interface, several features currently use **rule-based or template-based logic** rather than a connected Large Language Model.

For example:

* Resume matching → cosine similarity
* Missing keywords → regex/set comparison
* Job title extraction → keyword-based detection
* Salary prediction → rule-based calculation
* Bullet rewriting → predefined examples
* HR outreach → templates
* Mock interview feedback → predefined feedback

This makes the project lightweight and easy to run without an external AI API.

---

## 🚀 Future Improvements

Possible future enhancements include:

### 🤖 Real AI Integration

* OpenAI API integration
* Gemini API integration
* Local LLM support
* AI-powered resume rewriting
* Semantic resume/JD matching

### 📊 Better ATS Analysis

* TF-IDF keyword scoring
* Sentence embeddings
* Semantic similarity
* Skill extraction
* Job-title normalization
* ATS formatting checks
* Section detection

### 💼 Advanced Job Search

* Real-time job APIs
* Location-based filtering
* Experience-level filtering
* Remote/hybrid filtering
* Salary-based filtering

### 💰 Improved Salary Prediction

* Real salary datasets
* Experience
* Location
* Job title
* Company size
* Industry
* Technology stack

### 🎤 Advanced Mock Interview

* Dynamic AI-generated questions
* Role-specific technical questions
* Behavioral questions
* Answer scoring
* Communication analysis
* STAR-method feedback
* Follow-up questions

### 📄 Resume Export

* Direct PDF generation
* DOCX export
* Multiple professional templates
* ATS-friendly formatting
* One-page/two-page optimization

---

## 🔐 Privacy

This application is designed as a local Streamlit application.

Uploaded resumes and Job Descriptions are processed by the running application. If the project is deployed publicly, review the hosting platform's data-handling policies and avoid uploading sensitive personal information unless appropriate safeguards are implemented.

---

## ⚠️ Disclaimer

This project is intended for **educational and career-assistance purposes**.

The following outputs should be treated as estimates or suggestions rather than authoritative results:

* Resume match scores
* Missing keywords
* Salary predictions
* AI-generated bullet points
* Job recommendations
* Interview feedback

Always verify important career, salary, and job-market information independently.

---

## 🤝 Contributing

Contributions are welcome!

### Steps

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature/new-feature
```

3. Make your changes.
4. Commit your changes:

```bash
git commit -m "Add new feature"
```

5. Push the branch:

```bash
git push origin feature/new-feature
```

6. Open a Pull Request.

---

## 📜 License

This project can be released under the **MIT License**.

If you use the MIT License, add a `LICENSE` file to the repository containing the standard MIT License text.

---

## 👨‍💻 Author

**Your Name**

Built with ❤️ using **Python + Streamlit**.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub!

```text
🚀 Analyze → ✏️ Build → 🎯 Optimize → 💰 Estimate → ✉️ Connect → 🎤 Practice
```

**Smart AI Resume Hub — Your all-in-one career toolkit.**
