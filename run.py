#!/usr/bin/env python3
"""
Smart Resume Matcher - Real Files Only
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from document_parser import DocumentParser
from matcher import ResumeJobMatcher
from utils import print_match_summary, save_results

def main():
    print("🤖 SMART RESUME MATCHER")
    print("=" * 50)
    print("Process real resume and job description files")
    print("=" * 50)
    
    # Get file paths from user
    print("\n📁 ENTER FILE PATHS:")
    print("-" * 30)
    
    resume_path = input("Path to RESUME (PDF/DOCX/TXT): ").strip()
    job_path = input("Path to JOB DESCRIPTION (PDF/DOCX/TXT): ").strip()
    
    if not resume_path:
        print("❌ Please provide a resume file path")
        return
    
    if not job_path:
        print("❌ Please provide a job description file path")
        return
    
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        return
    
    if not os.path.exists(job_path):
        print(f"❌ Job file not found: {job_path}")
        return
    
    # Initialize
    print("\n🔧 Initializing...")
    parser = DocumentParser()
    matcher = ResumeJobMatcher()
    
    # Process files
    try:
        print(f"📄 Reading files...")
        
        # Extract text based on file type
        resume_text = parser.extract_text(resume_path, resume_path.split('.')[-1].lower())
        job_text = parser.extract_text(job_path, job_path.split('.')[-1].lower())
        
        if not resume_text.strip():
            print(f"❌ Could not extract text from resume. File might be empty or corrupted.")
            return
            
        if not job_text.strip():
            print(f"❌ Could not extract text from job description. File might be empty or corrupted.")
            return
        
        print(f"✓ Resume text: {len(resume_text)} characters")
        print(f"✓ Job text: {len(job_text)} characters")
        
        # Parse
        print("📊 Parsing documents...")
        resume_data = parser.parse_resume(resume_text)
        job_data = parser.parse_job_description(job_text)
        
        print(f"✓ Found {len(resume_data['skills'])} skills in resume")
        print(f"✓ Found {len(job_data['required_skills'])} required job skills")
        print(f"✓ Found {len(job_data['preferred_skills'])} preferred job skills")
        
        # Calculate match
        print("\n🔍 Calculating match...")
        match_result = matcher.match(resume_data, job_data, None, None)
        
        # Display results
        print_match_summary(match_result)
        
        # Generate analysis
        print("\n📝 ANALYSIS:")
        overall = match_result['overall_score']
        skill_details = match_result['skill_details']
        
        # Match rating
        if overall >= 90:
            print("✅ EXCELLENT MATCH - Highly recommended")
        elif overall >= 80:
            print("👍 STRONG MATCH - Recommend interview")
        elif overall >= 70:
            print("⚠️  GOOD MATCH - Consider for interview")
        elif overall >= 50:
            print("⚠️  FAIR MATCH - Review other candidates first")
        else:
            print("❌ WEAK MATCH - Not recommended")
        
        # Skill analysis
        print(f"\n🔧 Skills Analysis:")
        print(f"   ✅ Required matches: {len(skill_details['required_matches'])}/{len(job_data['required_skills'])}")
        if skill_details['required_matches']:
            print(f"      Matched: {', '.join(skill_details['required_matches'][:5])}")
        
        if skill_details['missing_required']:
            print(f"   ❌ Missing: {', '.join(skill_details['missing_required'][:3])}")
        
        # Experience analysis
        print(f"\n⏳ Experience Analysis:")
        resume_years = resume_data.get('experience_years', 0)
        job_years = job_data.get('experience_required', 0)
        
        if resume_years >= job_years:
            print(f"   ✅ Meets requirement: {resume_years} years (vs {job_years} required)")
        else:
            print(f"   ⚠️  Below requirement: {resume_years} years (vs {job_years} required)")
        
        # Save results
        results = {
            'resume_file': resume_path,
            'job_file': job_path,
            'resume_data': resume_data,
            'job_data': job_data,
            'match_result': match_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Create outputs directory
        os.makedirs('outputs', exist_ok=True)
        
        # Generate output filename
        resume_name = os.path.splitext(os.path.basename(resume_path))[0]
        job_name = os.path.splitext(os.path.basename(job_path))[0]
        output_file = f"outputs/match_{resume_name}_vs_{job_name}.json"
        
        if save_results(results, output_file):
            print(f"\n💾 Results saved to: {output_file}")
            
            # Also save a text summary
            summary_file = f"outputs/match_summary_{resume_name}_vs_{job_name}.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Resume Match Analysis\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Resume: {resume_path}\n")
                f.write(f"Job: {job_path}\n")
                f.write(f"\nOverall Match Score: {match_result['overall_score']:.1f}%\n")
                f.write(f"\nAnalysis:\n")
                f.write(f"Skills matched: {len(skill_details['required_matches'])}/{len(job_data['required_skills'])} required\n")
                f.write(f"Experience: {resume_years} years vs {job_years} required\n")
                f.write(f"\nMatched skills: {', '.join(skill_details['required_matches'])}\n")
            
            print(f"📝 Summary saved to: {summary_file}")
        
        print("\n" + "="*50)
        print("✅ PROCESS COMPLETED!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()