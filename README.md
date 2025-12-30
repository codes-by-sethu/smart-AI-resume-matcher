I need to update your README because **it's incorrect** - the commands it shows don't work with your actual Flask app. Here's the corrected version:

## 📝 **Updated README.md**

```markdown
# Smart AI Resume Matcher 🤖📄

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)

## 🚀 Overview

**Smart AI Resume Matcher** is an AI-powered web application that intelligently matches resumes with job descriptions. It goes beyond simple keyword matching by leveraging semantic embeddings, skill extraction, and weighted scoring for accurate candidate-job alignment.

## ✨ Features

* **Semantic AI Matching:** Uses BERT-based embeddings for contextual understanding
* **Multi-format Support:** PDF, DOCX, TXT document parsing
* **Dynamic Skill Extraction:** 100+ technical & soft skills database
* **Weighted Scoring:** Configurable weights for skills, experience, education
* **AI Explanations:** Human-readable match insights and recommendations
* **Web Interface:** User-friendly Flask-based web application
* **REST API:** Programmatic access to matching engine

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/codes-by-sethu/smart-AI-resume-matcher.git
cd smart-AI-resume-matcher

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs data
```

## 🚀 Quick Start

### **Web Application (Recommended)**
```bash
# Start the Flask web server
python app.py

# Open browser and navigate to:
# http://127.0.0.1:5000
```

### **API Usage**
```bash
# Health check
curl http://127.0.0.1:5000/health

# Upload and match (using curl)
curl -X POST -F "resume=@your_resume.pdf" -F "job_text=Python Developer with 3+ years experience..." http://localhost:5000/upload

# Or upload job description file
curl -X POST -F "resume=@resume.pdf" -F "job_description=@job.pdf" http://localhost:5000/upload
```

### **Debug/Testing Tool**
```bash
# Run comprehensive debug analysis
python debug_skills.py

# Or specify custom files
python debug_skills.py path/to/resume.txt path/to/job.txt
```

## 📁 Project Structure

```
smart-resume-matcher/
├── app.py                    # Main Flask web application
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── debug_skills.py          # Debug and testing tool
├── sample_match_results.json # Example output
├── setup.py                 # Package configuration
├── src/                     # Core AI modules
│   ├── __init__.py
│   ├── ai_explainer.py     # AI explanation generator
│   ├── document_parser.py  # Document parsing and skill extraction
│   ├── embedding_generator.py # Semantic embedding generator
│   ├── matcher.py          # Matching engine with weighted scoring
│   └── utils.py            # Utility functions
├── static/                  # Web assets (CSS, JS, images)
├── templates/               # HTML templates
├── tests/                   # Test files
├── uploads/                 # Temporary upload storage
├── outputs/                 # Match result storage
└── data/                    # Sample data files
```

## 🔧 Configuration

### **Matching Weights**
Edit `src/matcher.py` to adjust scoring weights:

```python
weights = {
    'required_skills': 0.35,    # Most critical: Required skills match
    'preferred_skills': 0.20,   # Bonus for having preferred skills
    'experience': 0.25,         # Years of experience match
    'education': 0.15,          # Educational qualifications
    'semantic': 0.05            # Contextual/semantic similarity
}
```

### **Skill Keywords**
Extend skill recognition in `src/document_parser.py`:

```python
skill_keywords = {
    'programming': ['python', 'java', 'c++', 'sql', 'javascript', 'r', 'go'],
    'cloud': ['aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform'],
    'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
    'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn']
}
```

## 🌐 Web Interface Guide

1. **Access the application** at `http://127.0.0.1:5000`
2. **Upload your resume** (PDF, DOCX, or TXT format)
3. **Provide job description** (upload file or paste text)
4. **Click "Analyze Match"** to get AI-powered analysis
5. **Review results** including:
   - Overall match score
   - Skill matching breakdown
   - Missing skills identification
   - AI-generated recommendations
   - Improvement suggestions

## 📊 Sample Output

```json
{
  "overall_score": 90.0,
  "skill_score": 76.7,
  "experience_score": 100.0,
  "education_score": 100.0,
  "semantic_score": 63.8,
  "ai_explanation": "🎯 EXCELLENT MATCH - This candidate strongly aligns with all job requirements...",
  "recommendation": "Strong candidate, recommend immediate interview"
}
```

## 🧪 Testing & Debugging

```bash
# Run comprehensive debug
python debug_skills.py

# Run tests (if available)
python -m pytest tests/ -v

# Test API endpoints
curl http://127.0.0.1:5000/health
```

## 🔍 How It Works

1. **Document Parsing**: Extracts text from resumes and job descriptions
2. **Skill Extraction**: Identifies 100+ technical and soft skills
3. **Semantic Embedding**: Creates AI embeddings for contextual understanding
4. **Weighted Scoring**: Calculates match score using configurable weights
5. **AI Analysis**: Generates human-readable explanations and recommendations

## 🛠️ Technology Stack

- **Backend**: Flask, Python
- **AI/ML**: Sentence Transformers, scikit-learn, NumPy
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: HTML5, CSS3, JavaScript
- **Embeddings**: BERT-based semantic models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

## 👥 Authors

- **Sethulakshmi Kochuchiraiyil Babu**
- **Man Vijaybhai Patel**
- **Luthfi Juneeda Shaj**
- **Yasar Thajudeen**

*"Matching talent with opportunity intelligently."*
```