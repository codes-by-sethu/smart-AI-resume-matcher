#!/usr/bin/env python3
"""
COMPREHENSIVE DEBUG SCRIPT FOR SMART RESUME-JOB MATCHER
Project 4: AI-Powered Resume and Job Matching System
"""
import sys
import os
import json
import re
import numpy as np
from typing import Dict, List, Any, Tuple

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import your components
from document_parser import DocumentParser
from matcher import ResumeJobMatcher
from embedding_generator import EmbeddingGenerator
from ai_explainer import AIExplainer
from utils import save_results

class ProjectDebugger:
    """Debugger for the Smart Resume-Job Matcher Project"""
    
    def __init__(self):
        self.components = {}
        self.test_data = {}
        self.debug_results = {}
        
    def load_components(self):
        """Load all project components"""
        print("🚀 Loading project components...")
        
        try:
            self.components['parser'] = DocumentParser()
            print("  ✅ DocumentParser loaded")
        except Exception as e:
            print(f"  ❌ DocumentParser failed: {e}")
            
        try:
            self.components['matcher'] = ResumeJobMatcher()
            print("  ✅ ResumeJobMatcher loaded")
        except Exception as e:
            print(f"  ❌ ResumeJobMatcher failed: {e}")
            
        try:
            self.components['embedder'] = EmbeddingGenerator()
            print("  ✅ EmbeddingGenerator loaded")
        except Exception as e:
            print(f"  ❌ EmbeddingGenerator failed: {e}")
            
        try:
            self.components['explainer'] = AIExplainer()
            print("  ✅ AIExplainer loaded")
        except Exception as e:
            print(f"  ❌ AIExplainer failed: {e}")
            
        return all(self.components.values())
    
    def load_test_files(self, resume_path: str, job_path: str):
        """Load test files"""
        print(f"\n📂 Loading test files...")
        
        try:
            with open(resume_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.test_data['resume_text'] = f.read()
            print(f"  ✅ Resume loaded: {len(self.test_data['resume_text'])} chars")
            
            with open(job_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.test_data['job_text'] = f.read()
            print(f"  ✅ Job description loaded: {len(self.test_data['job_text'])} chars")
            
            return True
        except Exception as e:
            print(f"  ❌ Failed to load files: {e}")
            return False
    
    def test_parsing(self):
        """Test document parsing"""
        print("\n" + "="*60)
        print("PHASE 1: DOCUMENT PARSING ANALYSIS")
        print("="*60)
        
        parser = self.components['parser']
        
        # Parse documents
        print("\n📄 PARSING RESUME:")
        resume_data = parser.parse_resume(self.test_data['resume_text'])
        self.debug_results['resume_data'] = resume_data
        
        print(f"  Skills extracted: {len(resume_data['skills'])}")
        print(f"  Sample skills: {resume_data['skills'][:10]}")
        print(f"  Experience years: {resume_data['experience_years']}")
        print(f"  Education: {resume_data['education']}")
        
        print("\n📄 PARSING JOB DESCRIPTION:")
        job_data = parser.parse_job_description(self.test_data['job_text'])
        self.debug_results['job_data'] = job_data
        
        print(f"  Required skills: {len(job_data['required_skills'])}")
        print(f"  Sample required: {job_data['required_skills'][:10]}")
        print(f"  Preferred skills: {len(job_data['preferred_skills'])}")
        print(f"  Sample preferred: {job_data['preferred_skills'][:5]}")
        print(f"  Experience required: {job_data['experience_required']}")
        
        # Detailed skill analysis
        print("\n🔍 SKILL EXTRACTION ANALYSIS:")
        
        # Check if skills are being extracted properly
        print(f"\n  Resume skills list (first 15):")
        for i, skill in enumerate(resume_data['skills'][:15], 1):
            print(f"    {i:2}. {skill}")
            
        print(f"\n  Job required skills (all):")
        for i, skill in enumerate(job_data['required_skills'], 1):
            print(f"    {i:2}. {skill}")
            
        print(f"\n  Job preferred skills (all):")
        for i, skill in enumerate(job_data['preferred_skills'], 1):
            print(f"    {i:2}. {skill}")
        
        return resume_data, job_data
    
    def test_embeddings(self, resume_data: Dict, job_data: Dict):
        """Test embedding generation"""
        print("\n" + "="*60)
        print("PHASE 2: EMBEDDING GENERATION")
        print("="*60)
        
        embedder = self.components['embedder']
        
        # Generate embeddings for resume summary and job description
        print("\n🤖 GENERATING EMBEDDINGS:")
        
        try:
            resume_summary = resume_data['summary']
            job_summary = job_data.get('summary', self.test_data['job_text'][:1000])
            
            print(f"  Generating resume embedding...")
            resume_embedding = embedder.get_embedding(resume_summary)
            print(f"  Resume embedding shape: {resume_embedding.shape}")
            
            print(f"  Generating job embedding...")
            job_embedding = embedder.get_embedding(job_summary)
            print(f"  Job embedding shape: {job_embedding.shape}")
            
            # Calculate semantic similarity
            semantic_score = embedder.get_similarity(resume_embedding, job_embedding)
            print(f"  Semantic similarity score: {semantic_score:.3f}")
            
            self.debug_results['embeddings'] = {
                'resume_shape': resume_embedding.shape,
                'job_shape': job_embedding.shape,
                'semantic_score': semantic_score
            }
            
            return resume_embedding, job_embedding, semantic_score
            
        except Exception as e:
            print(f"  ❌ Embedding generation failed: {e}")
            print(f"  Using fallback embeddings...")
            
            # Create dummy embeddings for testing
            resume_embedding = np.random.randn(384).astype(np.float32)
            job_embedding = np.random.randn(384).astype(np.float32)
            semantic_score = 0.5
            
            return resume_embedding, job_embedding, semantic_score
    
    def test_matching(self, resume_data: Dict, job_data: Dict, 
                     resume_embedding: np.ndarray, job_embedding: np.ndarray,
                     semantic_score: float):
        """Test matching logic"""
        print("\n" + "="*60)
        print("PHASE 3: MATCHING LOGIC")
        print("="*60)
        
        matcher = self.components['matcher']
        
        print("\n🎯 RUNNING MATCHING ALGORITHM:")
        
        # First, manually check skill matching
        print("\n🔍 MANUAL SKILL MATCHING CHECK:")
        
        resume_skills = set(skill.lower().strip() for skill in resume_data['skills'])
        required_skills = set(skill.lower().strip() for skill in job_data['required_skills'])
        preferred_skills = set(skill.lower().strip() for skill in job_data['preferred_skills'])
        
        required_matches = resume_skills.intersection(required_skills)
        preferred_matches = resume_skills.intersection(preferred_skills)
        
        print(f"  Resume skills count: {len(resume_skills)}")
        print(f"  Required skills count: {len(required_skills)}")
        print(f"  Preferred skills count: {len(preferred_skills)}")
        print(f"  Required matches found: {len(required_matches)}")
        print(f"  Preferred matches found: {len(preferred_matches)}")
        
        if required_matches:
            print(f"  Matched required skills: {list(required_matches)}")
        else:
            print("  ⚠️  NO REQUIRED SKILLS MATCHED!")
            
        # Check each required skill individually
        print("\n  Required skills matching breakdown:")
        for skill in sorted(required_skills):
            in_resume = skill in resume_skills
            status = "✓" if in_resume else "✗"
            print(f"    {status} {skill}")
        
        # Run the actual matcher
        print("\n🤖 RUNNING RESUMEJOBMATCHER:")
        match_result = matcher.match(
            resume_data, 
            job_data, 
            resume_embedding, 
            job_embedding
        )
        
        self.debug_results['match_result'] = match_result
        
        # Display results
        print(f"\n📊 MATCH RESULTS:")
        print(f"  Overall Score: {match_result['overall_score']:.1f}%")
        print(f"  Skill Score: {match_result['skill_score']:.1f}%")
        print(f"  Experience Score: {match_result['experience_score']:.1f}%")
        print(f"  Education Score: {match_result['education_score']:.1f}%")
        print(f"  Semantic Score: {match_result['semantic_score']:.1f}%")
        
        # Display skill details
        skill_details = match_result['skill_details']
        print(f"\n🔧 SKILL DETAILS:")
        print(f"  Required matches: {skill_details['required_coverage']}")
        print(f"  Preferred matches: {skill_details['preferred_coverage']}")
        print(f"  Missing required: {len(skill_details['missing_required'])}")
        if skill_details['missing_required']:
            print(f"    - {skill_details['missing_required']}")
        
        return match_result
    
    def test_explanation(self, resume_data: Dict, job_data: Dict, match_result: Dict):
        """Test AI explanation generation"""
        print("\n" + "="*60)
        print("PHASE 4: AI EXPLANATION GENERATION")
        print("="*60)
        
        explainer = self.components['explainer']
        
        print("\n🤖 GENERATING AI EXPLANATION:")
        
        try:
            explanation = explainer.generate_match_explanation(
                resume_data, 
                job_data, 
                match_result
            )
            
            print("\n💡 EXPLANATION GENERATED:")
            print("-" * 40)
            print(explanation)
            print("-" * 40)
            
            self.debug_results['explanation'] = explanation
            
            return explanation
            
        except Exception as e:
            print(f"  ❌ Explanation generation failed: {e}")
            return None
    
    def analyze_issues(self):
        """Analyze and identify issues"""
        print("\n" + "="*60)
        print("PHASE 5: ISSUE ANALYSIS")
        print("="*60)
        
        print("\n🔍 IDENTIFYING POTENTIAL ISSUES:")
        
        issues = []
        
        # Check skill extraction
        resume_skills = self.debug_results.get('resume_data', {}).get('skills', [])
        job_required = self.debug_results.get('job_data', {}).get('required_skills', [])
        
        if len(resume_skills) == 0:
            issues.append("❌ No skills extracted from resume")
        if len(job_required) == 0:
            issues.append("❌ No required skills extracted from job description")
        
        # Check matching
        match_result = self.debug_results.get('match_result', {})
        if match_result.get('overall_score', 0) == 0:
            issues.append("❌ Overall match score is 0")
            
        skill_details = match_result.get('skill_details', {})
        if len(skill_details.get('required_matches', [])) == 0 and len(job_required) > 0:
            issues.append("⚠️  No required skills matched despite having requirements")
        
        # Display issues
        if issues:
            print("\n📋 IDENTIFIED ISSUES:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ No major issues identified")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("  1. Check skill keyword list in document_parser.py")
        print("  2. Verify skill normalization in matcher.py")
        print("  3. Ensure test files contain appropriate skills")
        print("  4. Check if embeddings are working properly")
        
        return issues
    
    def save_debug_report(self):
        """Save detailed debug report"""
        print("\n" + "="*60)
        print("SAVING DEBUG REPORT")
        print("="*60)
        
        # Save comprehensive report
        report = {
            'project': 'Smart Resume-Job Matcher',
            'debug_timestamp': np.datetime64('now').astype(str),
            'components_loaded': list(self.components.keys()),
            'test_data_info': {
                'resume_length': len(self.test_data.get('resume_text', '')),
                'job_length': len(self.test_data.get('job_text', ''))
            },
            'parsing_results': {
                'resume_skills_count': len(self.debug_results.get('resume_data', {}).get('skills', [])),
                'job_required_count': len(self.debug_results.get('job_data', {}).get('required_skills', [])),
                'job_preferred_count': len(self.debug_results.get('job_data', {}).get('preferred_skills', []))
            },
            'matching_results': {
                'overall_score': self.debug_results.get('match_result', {}).get('overall_score', 0),
                'skill_score': self.debug_results.get('match_result', {}).get('skill_score', 0),
                'required_matches': len(self.debug_results.get('match_result', {}).get('skill_details', {}).get('required_matches', [])),
                'missing_required': self.debug_results.get('match_result', {}).get('skill_details', {}).get('missing_required', [])
            },
            'full_debug_data': self.debug_results
        }
        
        # Save to file
        save_results(report, 'debug_report.json')
        print("✅ Debug report saved to: debug_report.json")
        
        # Also save a simplified version
        with open('debug_summary.txt', 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("DEBUG SUMMARY - Smart Resume-Job Matcher\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Overall Match Score: {report['matching_results']['overall_score']:.1f}%\n")
            f.write(f"Skills Matched: {report['matching_results']['required_matches']}/{report['parsing_results']['job_required_count']}\n\n")
            
            f.write("Missing Required Skills:\n")
            for skill in report['matching_results']['missing_required']:
                f.write(f"  - {skill}\n")
        
        print("✅ Debug summary saved to: debug_summary.txt")
    
    def run_complete_debug(self, resume_path: str, job_path: str):
        """Run complete debug pipeline"""
        print("🔍 SMART RESUME-JOB MATCHER - DEBUG MODE")
        print("Project: AI-Powered Resume and Job Matching System")
        print("="*80)
        
        # Load components
        if not self.load_components():
            print("❌ Failed to load components. Exiting.")
            return False
        
        # Load test files
        if not self.load_test_files(resume_path, job_path):
            print("❌ Failed to load test files. Exiting.")
            return False
        
        # Run all phases
        try:
            # Phase 1: Parsing
            resume_data, job_data = self.test_parsing()
            
            # Phase 2: Embeddings
            resume_emb, job_emb, semantic_score = self.test_embeddings(resume_data, job_data)
            
            # Phase 3: Matching
            match_result = self.test_matching(resume_data, job_data, resume_emb, job_emb, semantic_score)
            
            # Phase 4: Explanation
            self.test_explanation(resume_data, job_data, match_result)
            
            # Phase 5: Analysis
            self.analyze_issues()
            
            # Save report
            self.save_debug_report()
            
            print("\n" + "="*80)
            print("✅ DEBUG COMPLETED SUCCESSFULLY")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ DEBUG FAILED WITH ERROR: {e}")
            traceback.print_exc()
            return False

def main():
    """Main debug function"""
    debugger = ProjectDebugger()
    
    # Define test file paths
    resume_path = 'data/sample_resume.txt'
    job_path = 'data/sample_job.txt'
    
    # Alternative paths if data folder doesn't exist
    if not os.path.exists(resume_path):
        print(f"⚠️  {resume_path} not found. Using alternative paths...")
        
        # Try to find files
        possible_paths = [
            'sample_resume.txt',
            'test_resume.txt',
            'resume.txt',
            '../data/sample_resume.txt'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                resume_path = path
                break
        
        # If still not found, create a sample
        if not os.path.exists(resume_path):
            print("Creating sample resume...")
            with open('sample_resume.txt', 'w') as f:
                f.write("""
John Doe - Software Engineer
Summary: Experienced Python developer with 5 years in web development.
Skills: Python, Django, JavaScript, SQL, AWS, Docker, Git
Experience: 5 years as Senior Developer at TechCorp
Education: Bachelor of Science in Computer Science
                """)
            resume_path = 'sample_resume.txt'
    
    # Run debug
    success = debugger.run_complete_debug(resume_path, job_path)
    
    if success:
        print("\n🎉 Debug completed! Check the following files:")
        print("  - debug_report.json (detailed results)")
        print("  - debug_summary.txt (summary)")
        print("\nNext steps:")
        print("  1. Review the debug summary")
        print("  2. Check skill extraction in parsing phase")
        print("  3. Verify skill matching logic")
        print("  4. Test with different resume/job combinations")
    else:
        print("\n❌ Debug failed. Please check the errors above.")

if __name__ == "__main__":
    main()