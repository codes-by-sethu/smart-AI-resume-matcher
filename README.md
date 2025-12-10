# Smart AI Resume Matcher 🤖📄

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

**Smart AI Resume Matcher** uses AI to match resumes with jobs intelligently. It goes beyond keywords, leveraging semantic embeddings, skill extraction, and weighted scoring for accurate candidate-job alignment.

## ✨ Features

* **Semantic Matching:** Uses embeddings for contextual relevance.
* **Multi-format Support:** PDF, DOCX, TXT.
* **Dynamic Skill Extraction:** 100+ technical & soft skills.
* **Weighted Scoring:** Configurable for skills, experience, education, semantics.
* **AI Explanations:** Human-readable match insights.
* **Batch Processing:** Evaluate multiple resumes at once.
* **Detailed Logging & Analytics.**

## 📦 Installation

```bash
git clone https://github.com/codes-by-sethu/smart-AI-resume-matcher.git
cd smart-AI-resume-matcher
python -m venv venv
source venv/Scripts/activate   # Windows
pip install -r requirements.txt
mkdir uploads outputs data
```

## 🚀 Quick Start

**Single Resume-Job Matching:**

```bash
python app.py --resume data/sample_resume.txt --job data/sample_job.txt
```

**Batch Matching:**

```bash
python app.py --batch uploads/resumes/ --job data/sample_job.txt
```

**Interactive Mode:**

```bash
python app.py --interactive
```

## 📁 Project Structure

```
smart-resume-matcher/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── uploads/
├── outputs/
└── src/
    ├── document_parser.py
    ├── matcher.py
    ├── embedding_generator.py
    ├── ai_explainer.py
    └── utils.py
```

## 🔧 Configuration

Edit `src/matcher.py` to adjust weights:

```python
weights = {
    'required_skills': 0.35,
    'preferred_skills': 0.2,
    'experience': 0.25,
    'education': 0.15,
    'semantic': 0.05
}
```

Extend skill keywords in `src/document_parser.py`:

```python
skill_keywords = {
    'programming': ['python', 'java', 'c++', 'sql', 'javascript'],
    'cloud': ['aws', 'gcp', 'azure', 'docker', 'kubernetes']
}
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

## 📄 License

MIT License.

*"Matching talent with opportunity intelligently."*
