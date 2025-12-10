import json
import os
import re
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
import docx
import io
import uuid
import sys

# Fix JSON serialization for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.json_encoder = NumpyEncoder

# Add src directory to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(SRC_DIR)

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== GLOBALLY DEFINED COMPONENTS ==========
# Initialize these at module level to avoid scope issues

# Simple document parser (ALWAYS AVAILABLE)
class SimpleDocumentParser:
    @staticmethod
    def parse_pdf(file_stream):
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PDF parsing error: {e}")
            return ""
    
    @staticmethod
    def parse_docx(file_stream):
        try:
            doc = docx.Document(file_stream)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"DOCX parsing error: {e}")
            return ""
    
    @staticmethod
    def parse_text(file_stream):
        try:
            text = file_stream.read().decode('utf-8')
            return text
        except Exception as e:
            print(f"Text parsing error: {e}")
            return ""

# Initialize simple parser (ALWAYS AVAILABLE)
simple_parser = SimpleDocumentParser()

# Try to import AI components
USE_AI_COMPONENTS = False
ai_parser = None
ai_embedder = None
ai_matcher = None
ai_explainer = None

try:
    from document_parser import DocumentParser as AIDocumentParser
    from matcher import MatchingEngine
    from embedding_generator import EmbeddingGenerator
    from ai_explainer import AIExplainer
    
    # Initialize AI components
    ai_parser = AIDocumentParser()
    ai_embedder = EmbeddingGenerator()
    ai_matcher = MatchingEngine()
    ai_explainer = AIExplainer()
    
    print("✅ AI backend components initialized successfully")
    USE_AI_COMPONENTS = True
    
except ImportError as e:
    print(f"⚠️ Failed to import AI components: {e}")
    print("⚠️ Will use simplified components instead")
    
    # Define fallback components
    class SimpleEmbeddingGenerator:
        @staticmethod
        def get_embedding(text: str) -> np.ndarray:
            """Generate a simple embedding for demo purposes"""
            words = re.findall(r'\b\w+\b', text.lower())
            unique_words = list(set(words[:100]))
            
            if len(unique_words) > 0:
                # Create deterministic embedding based on text hash
                seed = hash(text) % 10000
                np.random.seed(seed)
                embedding = np.random.randn(384).astype(np.float32)
                # Normalize
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                return embedding
            else:
                return np.zeros(384, dtype=np.float32)
        
        @staticmethod
        def get_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
            if emb1 is None or emb2 is None:
                return 0.0
            dot = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot / (norm1 * norm2))
    
    class SimpleMatcher:
        def __init__(self, weights: Optional[Dict[str, float]] = None):
            self.weights = weights or {
                'required_skills': 0.35,
                'preferred_skills': 0.20,
                'experience': 0.25,
                'education': 0.15,
                'semantic': 0.05
            }
        
        def match(self, resume_data: Dict, job_data: Dict, 
                 resume_embedding: Optional[np.ndarray] = None, 
                 job_embedding: Optional[np.ndarray] = None) -> Dict:
            
            resume_skills = resume_data.get('skills', [])
            job_required = job_data.get('required_skills', [])
            job_preferred = job_data.get('preferred_skills', [])
            resume_years = resume_data.get('experience_years', 0)
            job_years = job_data.get('experience_required', 0)
            resume_edu = resume_data.get('education', [])
            job_edu = job_data.get('education_required', [])
            
            # Skill matching
            resume_set = set(skill.lower().strip() for skill in resume_skills)
            required_set = set(skill.lower().strip() for skill in job_required)
            preferred_set = set(skill.lower().strip() for skill in job_preferred)
            
            required_matches = resume_set.intersection(required_set)
            required_score = len(required_matches) / len(required_set) if required_set else 1.0
            
            preferred_matches = resume_set.intersection(preferred_set)
            preferred_score = len(preferred_matches) / len(preferred_set) if preferred_set else 1.0
            
            if required_set:
                skill_score = (required_score * 0.7) + (preferred_score * 0.3)
            else:
                skill_score = preferred_score
            
            # Experience matching
            if job_years == 0:
                exp_score = 1.0
            elif resume_years >= job_years:
                excess_years = resume_years - job_years
                bonus = min(excess_years * 0.1, 0.3)
                exp_score = 1.0 + bonus
            else:
                base_score = resume_years / job_years
                exp_score = base_score * 0.8 if base_score < 0.5 else base_score
            
            # Education matching
            if not job_edu:
                edu_score = 1.0
            elif not resume_edu:
                edu_score = 0.0
            else:
                resume_lower = [e.lower() for e in resume_edu]
                job_lower = [e.lower() for e in job_edu]
                
                for edu in resume_lower:
                    for required in job_lower:
                        if required in edu or edu in required:
                            edu_score = 1.0
                            break
                    else:
                        continue
                    break
                else:
                    edu_score = 0.5
            
            # Semantic similarity
            semantic_score = 0.0
            if resume_embedding is not None and job_embedding is not None:
                dot = np.dot(resume_embedding, job_embedding)
                norm1 = np.linalg.norm(resume_embedding)
                norm2 = np.linalg.norm(job_embedding)
                if norm1 > 0 and norm2 > 0:
                    semantic_score = dot / (norm1 * norm2)
            
            # Overall score
            overall_score = (
                self.weights['required_skills'] * required_score +
                self.weights['preferred_skills'] * preferred_score +
                self.weights['experience'] * min(exp_score, 1.3) +
                self.weights['education'] * edu_score +
                self.weights['semantic'] * semantic_score
            ) * 100
            
            result = {
                'overall_score': float(min(max(overall_score, 0), 100)),
                'skill_score': float(skill_score * 100),
                'experience_score': float(min(exp_score, 1.3) * 100),
                'education_score': float(edu_score * 100),
                'semantic_score': float(semantic_score * 100),
                'skill_details': {
                    'score': float(skill_score * 100),
                    'required_matches': list(required_matches),
                    'preferred_matches': list(preferred_matches),
                    'missing_required': list(required_set - resume_set),
                    'missing_preferred': list(preferred_set - resume_set),
                    'required_coverage': f"{len(required_matches)}/{len(job_required)}",
                    'preferred_coverage': f"{len(preferred_matches)}/{len(job_preferred)}"
                },
                'match_breakdown': {
                    'skills_match': f"{len(required_matches)}/{len(job_required)} required skills",
                    'experience_match': f"{resume_years}/{job_years} years",
                    'education_match': "Exceeds" if edu_score > 1.0 else ("Meets" if edu_score >= 0.8 else "Partial"),
                    'semantic_match': f"{semantic_score:.2%}"
                }
            }
            
            return result
    
    class SimpleAIExplainer:
        @staticmethod
        def generate_match_explanation(resume_data: Dict, job_data: Dict, match_result: Dict) -> str:
            score = match_result.get('overall_score', 0)
            skill_details = match_result.get('skill_details', {})
            
            required_matches = skill_details.get('required_matches', [])
            missing_required = skill_details.get('missing_required', [])
            
            if score >= 90:
                return "🎯 **EXCELLENT MATCH** - This candidate strongly aligns with all job requirements.\n**Key Strengths:** Complete skill overlap, exceeds experience requirements.\n**Recommendation:** Highly recommended for immediate interview consideration."
            elif score >= 80:
                return "✅ **STRONG MATCH** - Candidate meets most requirements with excellent core skills.\n**Strengths:** Strong foundation in key required areas.\n**Recommendation:** Strong candidate worth interviewing."
            elif score >= 70:
                return "⚠️ **GOOD MATCH** - Candidate has relevant experience with some skill gaps.\n**Strengths:** Has most required skills and meets experience requirements.\n**Gaps:** Missing some preferred skills.\n**Recommendation:** Consider if other candidates are unavailable."
            elif score >= 60:
                return "📊 **FAIR MATCH** - Candidate meets basic requirements but has significant gaps.\n**Strengths:** Has some required skills and meets minimum experience.\n**Gaps:** Missing critical required skills.\n**Recommendation:** Consider as backup candidate."
            else:
                return "❌ **POOR MATCH** - Significant gaps between candidate and job requirements.\n**Issues:** Missing critical required skills or insufficient experience.\n**Recommendation:** Not recommended for this role."
    
    # Initialize fallback components
    ai_embedder = SimpleEmbeddingGenerator()
    ai_matcher = SimpleMatcher()
    ai_explainer = SimpleAIExplainer()

except Exception as e:
    print(f"⚠️ Error initializing components: {e}")
    # Ensure fallback components are defined
    if ai_embedder is None:
        # Define minimal fallback
        class SimpleEmbeddingGenerator:
            @staticmethod
            def get_embedding(text: str) -> np.ndarray:
                return np.zeros(384, dtype=np.float32)
        
        ai_embedder = SimpleEmbeddingGenerator()
        ai_matcher = SimpleMatcher()
        ai_explainer = SimpleAIExplainer()

# ========== ROUTES ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_components_loaded': USE_AI_COMPONENTS,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/upload', methods=['POST'])
def upload_and_match():
    try:
        # Get inputs - can be either file OR text for job description
        resume_file = request.files.get('resume')
        job_file = request.files.get('job_description')
        job_text_input = request.form.get('job_text', '').strip()
        
        print(f"📥 Received inputs: Resume file={resume_file}, Job file={job_file}, Job text length={len(job_text_input)}")
        
        # Validate resume (required)
        if not resume_file:
            return jsonify({'error': 'Resume file is required'}), 400
        
        # Validate job description (either file or text is required)
        if not job_file and not job_text_input:
            return jsonify({'error': 'Please provide job description (upload file or enter text)'}), 400
        
        # Parse resume file
        resume_filename = resume_file.filename.lower()
        resume_file_stream = io.BytesIO(resume_file.read())
        resume_file.seek(0)  # Reset for AI parser if needed
        
        if resume_filename.endswith('.pdf'):
            resume_text = simple_parser.parse_pdf(resume_file_stream)
        elif resume_filename.endswith('.docx'):
            resume_text = simple_parser.parse_docx(resume_file_stream)
        elif resume_filename.endswith('.txt'):
            resume_text = simple_parser.parse_text(resume_file_stream)
        else:
            return jsonify({'error': 'Unsupported resume file format. Use PDF, DOCX, or TXT'}), 400
        
        if not resume_text or len(resume_text.strip()) < 10:
            return jsonify({'error': 'Resume file is empty or could not be parsed'}), 400
        
        # Get job description text (from file or text input)
        job_desc_text = ""
        job_source = "text_input"  # Track source for response
        
        if job_file:
            # Parse job description file
            job_filename = job_file.filename.lower()
            job_file_stream = io.BytesIO(job_file.read())
            job_file.seek(0)  # Reset for AI parser
            
            if job_filename.endswith('.pdf'):
                job_desc_text = simple_parser.parse_pdf(job_file_stream)
            elif job_filename.endswith('.docx'):
                job_desc_text = simple_parser.parse_docx(job_file_stream)
            elif job_filename.endswith('.txt'):
                job_desc_text = simple_parser.parse_text(job_file_stream)
            else:
                return jsonify({'error': 'Unsupported job description file format. Use PDF, DOCX, or TXT'}), 400
            
            job_source = "file_upload"
        else:
            # Use text input
            job_desc_text = job_text_input
            job_source = "text_input"
        
        if not job_desc_text or len(job_desc_text.strip()) < 10:
            return jsonify({'error': 'Job description is too short or empty'}), 400
        
        print(f"📊 Text lengths: Resume={len(resume_text)} chars, Job={len(job_desc_text)} chars (Source: {job_source})")
        
        # Use AI components if available, otherwise use fallback
        if USE_AI_COMPONENTS and ai_parser is not None:
            print("🤖 Using AI backend components for parsing and matching...")
            
            try:
                # Parse with AI Document Parser
                resume_data = ai_parser.parse_resume(resume_text)
                job_data = ai_parser.parse_job_description(job_desc_text)
                
                # Generate embeddings
                resume_embedding = ai_embedder.get_embedding(resume_text[:1000])
                job_embedding = ai_embedder.get_embedding(job_desc_text[:1000])
                
            except Exception as ai_error:
                print(f"⚠️ AI parsing failed, using fallback: {ai_error}")
                resume_data, job_data = fallback_parsing(resume_text, job_desc_text)
                resume_embedding = ai_embedder.get_embedding(resume_text[:1000])
                job_embedding = ai_embedder.get_embedding(job_desc_text[:1000])
        else:
            print("⚠️ Using fallback parsing...")
            resume_data, job_data = fallback_parsing(resume_text, job_desc_text)
            resume_embedding = ai_embedder.get_embedding(resume_text[:1000])
            job_embedding = ai_embedder.get_embedding(job_desc_text[:1000])
        
        print(f"🔍 Parsed: Resume skills={len(resume_data.get('skills', []))}, "
              f"Job required={len(job_data.get('required_skills', []))}")
        
        # Perform matching
        match_result = ai_matcher.match(
            resume_data=resume_data,
            job_data=job_data,
            resume_embedding=resume_embedding,
            job_embedding=job_embedding
        )
        
        # Generate AI explanation
        explanation = ai_explainer.generate_match_explanation(
            resume_data=resume_data,
            job_data=job_data,
            match_result=match_result
        )
        
        # Create response
        response_data = {
            'success': True,
            'ai_components_used': USE_AI_COMPONENTS,
            'job_description_source': job_source,
            'resume_info': {
                'filename': resume_file.filename,
                'skills_count': len(resume_data.get('skills', [])),
                'skills': resume_data.get('skills', []),
                'experience_years': resume_data.get('experience_years', 0),
                'education': resume_data.get('education', [])
            },
            'job_info': {
                'source': job_source,
                'filename': job_file.filename if job_file else 'text_input',
                'required_skills': job_data.get('required_skills', []),
                'preferred_skills': job_data.get('preferred_skills', []),
                'experience_required': job_data.get('experience_required', 0),
                'education_required': job_data.get('education_required', [])
            },
            'match_result': match_result,
            'ai_explanation': explanation,
            'recommendation': get_recommendation(match_result['overall_score']),
            'match_quality': get_match_quality(match_result['overall_score'])
        }
        
        # Save to file for debugging
        save_match_result(response_data, resume_file.filename)
        
        print(f"✅ Matching completed successfully. Score: {match_result['overall_score']:.1f}%")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in upload_and_match: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Server error: {str(e)}',
            'details': traceback.format_exc() if app.debug else None
        }), 500
    

    
# ========== HELPER FUNCTIONS ==========
def fallback_parsing(resume_text: str, job_text: str) -> tuple:
    """Fallback parsing if AI components fail"""
    
    # Common skills list
    common_skills = [
        'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker', 
        'kubernetes', 'machine learning', 'ai', 'deep learning', 'tensorflow',
        'pytorch', 'git', 'github', 'ci/cd', 'agile', 'scrum', 'rest api',
        'node.js', 'react', 'angular', 'vue', 'flask', 'django', 'fastapi',
        'mongodb', 'postgresql', 'mysql', 'redis', 'linux', 'unix', 'bash',
        'powershell', 'html', 'css', 'typescript', 'c++', 'c#', '.net',
        'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'android', 'ios'
    ]
    
    # Parse resume
    resume_lower = resume_text.lower()
    extracted_skills = []
    for skill in common_skills:
        if skill in resume_lower:
            extracted_skills.append(skill)
    
    # Extract experience years from resume
    exp_patterns = [
        r'(\d+)\+?\s*years?\s+.*?experience',
        r'experience.*?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+.*?developer',
        r'(\d+)\+?\s*years?\s+.*?engineer'
    ]
    
    experience_years = 0
    for pattern in exp_patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if str(match).isdigit():
                years = int(match)
                if years > experience_years:
                    experience_years = years
                    break
    
    # Extract education from resume
    education_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'degree', 
                         'diploma', 'university', 'college', 'school', 'institute',
                         'bsc', 'msc', 'mba', 'ba', 'bs', 'ma', 'ms']
    education_lines = []
    for line in resume_text.split('\n'):
        if any(keyword in line.lower() for keyword in education_keywords):
            education_lines.append(line.strip())
    
    resume_data = {
        'skills': extracted_skills,
        'experience_years': experience_years,
        'education': education_lines[:3],
        'summary': resume_text[:500]
    }
    
    # Parse job description
    job_lower = job_text.lower()
    job_required = []
    job_preferred = []
    
    for skill in common_skills:
        if skill in job_lower:
            # Check context to determine if required or preferred
            skill_pos = job_lower.find(skill)
            context = job_lower[max(0, skill_pos-50):min(len(job_lower), skill_pos+len(skill)+50)]
            
            if any(word in context for word in ['required', 'must', 'essential', 'requirement']):
                job_required.append(skill)
            elif any(word in context for word in ['preferred', 'nice', 'bonus', 'plus']):
                job_preferred.append(skill)
            else:
                job_required.append(skill)  # Default to required
    
    # Remove duplicates
    job_required = list(set(job_required))
    job_preferred = list(set(job_preferred) - set(job_required))
    
    # Extract job experience requirement
    job_exp_matches = re.search(r'(\d+)\+?\s*years?\s+.*?experience', job_text, re.IGNORECASE)
    job_experience = float(job_exp_matches.group(1)) if job_exp_matches else 0
    
    job_data = {
        'required_skills': job_required,
        'preferred_skills': job_preferred,
        'experience_required': job_experience,
        'education_required': ['Bachelor Degree']  # Default
    }
    
    return resume_data, job_data

def get_recommendation(score: float) -> Dict:
    """Get recommendation based on match score"""
    if score >= 85:
        return {
            'level': 'Excellent',
            'text': 'Strong candidate, recommend immediate interview',
            'color': 'success',
            'icon': 'check-circle'
        }
    elif score >= 70:
        return {
            'level': 'Good',
            'text': 'Worth considering for interview',
            'color': 'info',
            'icon': 'thumbs-up'
        }
    elif score >= 50:
        return {
            'level': 'Moderate',
            'text': 'Consider if no better candidates',
            'color': 'warning',
            'icon': 'alert-circle'
        }
    else:
        return {
            'level': 'Poor',
            'text': 'Not recommended for this role',
            'color': 'danger',
            'icon': 'x-circle'
        }

def get_match_quality(score: float) -> str:
    """Get match quality description"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 50:
        return "Moderate"
    else:
        return "Poor"

def save_match_result(data: Dict, resume_filename: str):
    """Save match result to file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = re.sub(r'[^\w\-_]', '_', resume_filename)
        output_filename = f"match_result_{timestamp}_{safe_filename}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        
        print(f"💾 Result saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Failed to save result: {e}")
        return None

@app.route('/outputs/<filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# ========== MAIN ==========
if __name__ == '__main__':
    print("🚀 Starting Smart Resume Matcher Web Application...")
    print("=" * 60)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🤖 AI Components: {'Loaded ✅' if USE_AI_COMPONENTS else 'Fallback ⚠️'}")
    print("=" * 60)
    print("🌐 Web server running on: http://127.0.0.1:5000")
    print("📊 Health check: http://127.0.0.1:5000/health")
    print("=" * 60)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    app.run(debug=False, host='127.0.0.1', port=5000)