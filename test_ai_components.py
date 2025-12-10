#!/usr/bin/env python3
"""
Test AI components independently
"""
import os
import sys
import traceback

# Add src to path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(SRC_DIR)

print("🧪 TESTING AI COMPONENTS")
print("=" * 60)

# Test 1: Import components
print("1️⃣ Testing imports...")
try:
    from document_parser import DocumentParser
    from matcher import MatchingEngine
    from embedding_generator import EmbeddingGenerator
    from ai_explainer import AIExplainer
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create instances
print("\n2️⃣ Creating instances...")
try:
    parser = DocumentParser()
    matcher = MatchingEngine()
    embedder = EmbeddingGenerator()
    explainer = AIExplainer()
    print("✅ All instances created")
except Exception as e:
    print(f"❌ Instance creation failed: {e}")
    traceback.print_exc()

# Test 3: Test with sample text
print("\n3️⃣ Testing parsing with sample text...")
sample_resume = """John Doe - Software Engineer

SUMMARY:
Experienced software engineer with 5+ years in Python development.
Skills: Python, Django, JavaScript, SQL, AWS, Docker, Git.
Experience: 5 years at TechCorp.
Education: Bachelor of Computer Science.

PROJECTS:
- Built e-commerce platform using Django and React
- Developed microservices with Docker and Kubernetes
- Implemented CI/CD pipelines with Jenkins

CERTIFICATIONS:
AWS Certified Solutions Architect
"""

sample_job = """Senior Python Developer

REQUIRED SKILLS:
- Python (3+ years)
- Django or Flask
- SQL databases
- REST APIs
- Git

PREFERRED SKILLS:
- AWS
- Docker
- React
- CI/CD experience

EXPERIENCE REQUIRED:
3+ years professional experience

EDUCATION:
Bachelor's degree in Computer Science or related field
"""

try:
    # Parse resume
    resume_data = parser.parse_resume(sample_resume)
    print(f"✅ Resume parsed: {len(resume_data['skills'])} skills found")
    print(f"   Skills: {resume_data['skills']}")
    print(f"   Experience years: {resume_data['experience_years']}")
    
    # Parse job
    job_data = parser.parse_job_description(sample_job)
    print(f"✅ Job parsed: {len(job_data['required_skills'])} required skills")
    print(f"   Required: {job_data['required_skills']}")
    print(f"   Preferred: {job_data['preferred_skills']}")
    
except Exception as e:
    print(f"❌ Parsing failed: {e}")
    traceback.print_exc()

# Test 4: Test embeddings
print("\n4️⃣ Testing embeddings...")
try:
    embedding = embedder.get_embedding("Test text for embedding")
    print(f"✅ Embedding generated: shape={embedding.shape}")
except Exception as e:
    print(f"❌ Embedding failed: {e}")
    traceback.print_exc()

# Test 5: Test matching
print("\n5️⃣ Testing matching...")
try:
    if 'resume_data' in locals() and 'job_data' in locals():
        resume_emb = embedder.get_embedding(sample_resume[:1000])
        job_emb = embedder.get_embedding(sample_job[:1000])
        
        match_result = matcher.match(resume_data, job_data, resume_emb, job_emb)
        print(f"✅ Matching successful: {match_result['overall_score']:.1f}%")
        
        # Test explanation
        explanation = explainer.generate_match_explanation(resume_data, job_data, match_result)
        print(f"✅ Explanation generated: {len(explanation)} chars")
    else:
        print("⚠️ Skipping matching test (parsing failed)")
except Exception as e:
    print(f"❌ Matching failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)