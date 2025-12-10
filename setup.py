#!/usr/bin/env python3
"""
Setup script for Smart Resume-Job Matcher
Automatically installs dependencies and sets up the environment.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found!")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['uploads', 'results', 'data', 'src']
    
    print("📁 Creating directory structure...")
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"   Created/verified: {dir_path}")

def create_sample_files():
    """Create sample files for testing."""
    print("📄 Creating sample files...")
    
    # Create sample resume
    sample_resume = """John Doe - Senior Software Engineer

SUMMARY:
Experienced software engineer with 5+ years in full-stack development.
Specialized in Python, JavaScript, and cloud technologies.

SKILLS:
- Programming: Python, JavaScript, TypeScript, Java
- Frameworks: Django, React, Node.js, Spring Boot
- Databases: MySQL, PostgreSQL, MongoDB, Redis
- Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
- Tools: Git, Jenkins, Jira, Postman

EXPERIENCE:
Senior Software Engineer at TechCorp (2019-Present)
- Led development of microservices architecture
- Implemented CI/CD pipelines reducing deployment time by 40%
- Mentored 3 junior developers

Software Developer at Startup Inc. (2017-2019)
- Developed customer-facing web applications
- Optimized database queries improving performance by 30%

EDUCATION:
Master of Science in Computer Science
University of Technology, 2017

Bachelor of Science in Software Engineering
State University, 2015

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Google Cloud Professional Developer
"""
    
    # Create sample job description
    sample_job = """Senior Python Developer

JOB DESCRIPTION:
We are looking for a Senior Python Developer to join our team.
You will be responsible for developing and maintaining high-performance applications.

REQUIRED SKILLS:
- Python (3+ years experience)
- Django or Flask framework
- SQL databases (PostgreSQL/MySQL)
- REST API development
- Git version control
- Unit testing and debugging

PREFERRED SKILLS:
- AWS or Azure cloud services
- Docker containerization
- React or Angular frontend
- Microservices architecture
- CI/CD pipeline experience

EXPERIENCE REQUIRED:
- 3+ years of professional Python development
- Experience with web application development

EDUCATION REQUIREMENTS:
- Bachelor's degree in Computer Science or related field
- Relevant certifications are a plus

RESPONSIBILITIES:
- Design and develop scalable Python applications
- Collaborate with frontend developers
- Write clean, maintainable code
- Participate in code reviews
- Troubleshoot and debug applications
"""
    
    # Save sample files
    with open('data/sample_resume.txt', 'w', encoding='utf-8') as f:
        f.write(sample_resume)
    
    with open('data/sample_job.txt', 'w', encoding='utf-8') as f:
        f.write(sample_job)
    
    print("✅ Sample files created in 'data/' directory")

def setup_venv():
    """Create virtual environment (optional)."""
    response = input("\nCreate virtual environment? (y/n): ").strip().lower()
    if response == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            
            if platform.system() == "Windows":
                activate_cmd = "venv\\Scripts\\activate"
            else:
                activate_cmd = "source venv/bin/activate"
            
            print(f"\n✅ Virtual environment created!")
            print(f"\nTo activate:")
            print(f"  Windows:   {activate_cmd}")
            print(f"  macOS/Linux: {activate_cmd}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    return True

def main():
    """Main setup function."""
    print("=" * 60)
    print("SMART RESUME-JOB MATCHER - SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation failed. Trying alternative method...")
        try:
            # Try installing common packages individually
            packages = [
                "numpy>=1.21.0",
                "scikit-learn>=1.0.0",
                "sentence-transformers>=2.2.0",
                "PyPDF2>=2.0.0",
                "python-docx>=0.8.11"
            ]
            for package in packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("✅ Core packages installed successfully!")
        except Exception as e:
            print(f"❌ Failed to install core packages: {e}")
            print("\nPlease install dependencies manually:")
            print("  pip install numpy scikit-learn sentence-transformers PyPDF2 python-docx")
    
    # Setup virtual environment (optional)
    setup_venv()
    
    # Create sample files
    create_sample_files()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the application:")
    print("   python app.py --resume data/sample_resume.txt --job data/sample_job.txt")
    print("\n2. Run in interactive mode:")
    print("   python app.py --interactive")
    print("\n3. For debugging:")
    print("   python debug_project.py")
    print("\n4. Check logs:")
    print("   tail -f app.log")

if __name__ == "__main__":
    main()