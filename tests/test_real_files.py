#!/usr/bin/env python3
"""
Test with real PDF/DOCX files
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from document_parser import DocumentParser
from embedding_generator import EmbeddingGenerator
from matcher import ResumeJobMatcher
from ai_explainer import AIExplainer
from src.utils import safe_read_file, print_match_summary

def test_with_files(resume_path: str, job_path: str):
    """Test with actual files"""
    parser = DocumentParser()
    
    # Read files
    resume_content = safe_read_file(resume_path)
    job_content = safe_read_file(job_path)
    
    if not resume_content or not job_content:
        print("Error reading files")
        return
    
    # Get file types
    resume_type = resume_path.split('.')[-1].lower()
    job_type = job_path.split('.')[-1].lower()
    
    # Extract text
    resume_text = parser.extract_text(resume_content, resume_type)
    job_text = parser.extract_text(job_content, job_type)
    
    # Parse data
    resume_data = parser.parse_resume(resume_text)
    job_data = parser.parse_job_description(job_text)
    
    # Continue with matching...
    embedder = EmbeddingGenerator()
    matcher = ResumeJobMatcher()
    
    # Generate embeddings
    resume_embedding = embedder.get_embedding(resume_text[:2000])  # Limit text for speed
    job_embedding = embedder.get_embedding(job_text[:2000])
    
    # Calculate match
    match_result = matcher.match(
        resume_data, 
        job_data, 
        resume_embedding, 
        job_embedding
    )
    
    print_match_summary(match_result)
    
    return match_result

if __name__ == "__main__":
    # Example usage
    print("Testing with sample files...")
    
    # Create sample files if they don't exist
    import os
    
    # Create a sample resume text file
    sample_resume = """John Smith
Software Engineer
john.smith@email.com

SKILLS:
Programming: Python, Java, JavaScript, SQL
Frameworks: Django, React, Node.js
Databases: MySQL, MongoDB, PostgreSQL
Cloud: AWS, Docker, Kubernetes
Tools: Git, Jenkins, JIRA

EXPERIENCE:
Senior Software Engineer at TechCorp (2020-Present)
- Developed microservices using Python and Django
- Led team of 5 developers
- Implemented AWS infrastructure

Software Developer at StartupInc (2017-2020)
- Built web applications with React and Node.js
- Managed SQL databases

EDUCATION:
Bachelor of Science in Computer Science
University of Technology, 2013-2017

CERTIFICATIONS:
AWS Certified Solutions Architect
Python Institute Certified"""

    # Create a sample job description text file
    sample_job = """Software Engineer (Python)

Job Description:
We are looking for a skilled Software Engineer with Python experience.

Requirements:
- 3+ years of Python development experience
- Experience with web frameworks (Django/Flask)
- Strong knowledge of SQL databases
- AWS cloud experience
- Docker and Kubernetes knowledge

Required Skills:
- Python
- SQL
- AWS
- REST APIs
- Git

Preferred Skills:
- Docker
- Kubernetes
- React
- Microservices architecture

Education:
Bachelor's degree in Computer Science or related field

Experience:
Minimum 3 years of software development experience"""

    # Save sample files
    with open("sample_resume.txt", "w") as f:
        f.write(sample_resume)
    
    with open("sample_job.txt", "w") as f:
        f.write(sample_job)
    
    print("Created sample files: sample_resume.txt, sample_job.txt")
    
    # Test with the sample files
    result = test_with_files("sample_resume.txt", "sample_job.txt")
    
    print("\n✅ Test completed!")