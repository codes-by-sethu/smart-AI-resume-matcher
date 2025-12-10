import os
import re
import json
from typing import Dict, List, Set
import io

class DocumentParser:
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
        
    def _load_skill_keywords(self) -> Dict[str, List[str]]:
        """Load common skills database - ONLY definitions"""
        return {
            'programming': ['python', 'java', 'javascript', 'c++', 'sql', 'r', 'go', 'typescript', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'rust', 'scala'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'dynamodb', 'cassandra', 'firebase'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'vagrant'],
            'web_frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'node.js', 'express.js', 'spring', 'laravel', 'ruby on rails', 'asp.net', 'fastapi'],
            'methodologies': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'waterfall'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'postman', 'figma', 'trello', 'asana', 'github', 'gitlab'],
            'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'spark', 'hadoop', 'tableau', 'power bi', 'matplotlib', 'seaborn'],
            'mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical', 'critical thinking', 'time management']
        }
    
    def extract_text(self, file_path: str, ext: str) -> str:
        """Extract text from a file based on its extension"""
        ext = ext.lower()
        
        try:
            if ext == 'pdf':
                return self._extract_from_pdf(file_path)
            elif ext == 'docx':
                return self._extract_from_docx(file_path)
            elif ext in ['txt', 'pdf.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                # Try to read as text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            # Fallback if PyPDF2 not installed
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                return text
            except:
                return ""
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            return ""
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return ""
    
    def _find_skills_in_text(self, text: str) -> Set[str]:
        """Find skills in text dynamically"""
        text_lower = text.lower()
        found_skills = set()
        
        # Get all possible skills
        all_skills = []
        for category, skills in self.skill_keywords.items():
            all_skills.extend(skills)
        
        # Add compound skills
        compound_skills = ['rest api', 'microservices', 'ci/cd', 'machine learning', 'deep learning', 
                          'artificial intelligence', 'data mining', 'cloud computing', 'version control']
        all_skills.extend(compound_skills)
        
        # Skill variations mapping
        skill_variations = {
            'rest': 'rest api',
            'restful': 'rest api',
            'restapi': 'rest api',
            'mysql': 'sql',
            'postgresql': 'sql',
            'postgres': 'sql',
            'microsoft sql': 'sql',
            'ms sql': 'sql',
            'javascript': 'javascript',
            'js': 'javascript',
            'ecmascript': 'javascript',
            'react.js': 'react',
            'angularjs': 'angular',
            'vue.js': 'vue',
            'node': 'node.js',
            'express': 'express.js',
            'amazon web services': 'aws',
            'microsoft azure': 'azure',
            'google cloud platform': 'gcp',
            'google cloud': 'gcp',
            'cicd': 'ci/cd',
            'continuous integration': 'ci/cd',
            'docker container': 'docker',
            'kubernetes cluster': 'kubernetes',
            'k8s': 'kubernetes'
        }
        
        # Check for each skill
        for skill in all_skills:
            pattern = r'(^|\W)' + re.escape(skill) + r'($|\W)'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Check for skill variations
        for variation, canonical in skill_variations.items():
            pattern = r'(^|\W)' + re.escape(variation) + r'($|\W)'
            if re.search(pattern, text_lower):
                found_skills.add(canonical)
        
        return found_skills
    
    def parse_resume(self, text: str) -> Dict:
        """Parse resume text dynamically - NO HARDCODED DATA"""
        resume_data = {
            'skills': [],
            'experience': [],
            'education': [],
            'experience_years': 0,
            'summary': text[:500] + ("..." if len(text) > 500 else "")
        }
        
        # Find skills dynamically
        skills_found = self._find_skills_in_text(text)
        resume_data['skills'] = sorted(list(skills_found))
        
        # Extract experience years
        experience_years = 0
        
        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+.*?experience',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+.*?developer',
            r'(\d+)\+?\s*years?\s+.*?engineer',
            r'(\d+)\+?\s*years?\s+.*?professional',
            r'(\d+)\+?\s*years?\s+.*?work'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if str(match).isdigit():
                    years = int(match)
                    if years > experience_years:
                        experience_years = years
        
        # If no pattern found, look for year ranges
        if experience_years == 0:
            # Look for date ranges like "2018 - 2022"
            year_ranges = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|present|current|now)', text)
            if year_ranges:
                years_list = []
                for start, end in year_ranges:
                    try:
                        start_year = int(start)
                        if end.isdigit():
                            end_year = int(end)
                        else:
                            end_year = 2025  # Current year
                        
                        years_list.append(end_year - start_year)
                    except:
                        pass
                
                if years_list:
                    experience_years = max(years_list)
        
        resume_data['experience_years'] = experience_years
        
        # Extract education
        education = []
        edu_patterns = [
            r'(bachelor|b\.?s\.?|b\.?a\.?|b\.?tech|b\.?e\.?|b\.?com)\s+.*?\s+(in|of)?\s*([a-z\s&]+)',
            r'(master|m\.?s\.?|m\.?a\.?|m\.?tech|m\.?e\.?|mba)\s+.*?\s+(in|of)?\s*([a-z\s&]+)',
            r'(ph\.?d|doctorate|phd)\s+.*?\s+(in|of)?\s*([a-z\s&]+)',
            r'(associate|diploma|certificate)\s+.*?\s+(in|of)?\s*([a-z\s&]+)'
        ]
        
        for pattern in edu_patterns:
            matches = re.finditer(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 3:
                    edu = match.group(3).strip()
                    if edu and len(edu) > 3:
                        education.append(edu)
        
        resume_data['education'] = education
        
        return resume_data
    
    def parse_job_description(self, text: str) -> Dict:
        """Parse job description dynamically - NO HARDCODED DATA"""
        jd_data = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_required': 0,
            'education_required': []
        }
        
        text_lower = text.lower()
        
        # Extract experience requirement
        experience_required = 0
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+.*?experience',
            r'experience.*?(\d+)\+?\s*years?',
            r'minimum.*?(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s+.*?required',
            r'(\d+)\+?\s*years?\s+.*?minimum'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                exp = match.group(1)
                if exp.isdigit():
                    experience_required = int(exp)
                    break
        
        jd_data['experience_required'] = experience_required
        
        # Dynamic skill extraction
        required_skills = set()
        preferred_skills = set()
        
        # Get all skills
        all_skills = []
        for category, skills in self.skill_keywords.items():
            all_skills.extend(skills)
        
        # Add compound skills
        all_skills.extend(['rest api', 'microservices', 'ci/cd', 'machine learning'])
        
        # Skill variations mapping
        skill_cleanup = {
            'ci/cd': 'ci/cd',
            'cicd': 'ci/cd',
            'rest api': 'rest api',
            'restful api': 'rest api',
            'mysql': 'sql',
            'postgresql': 'sql',
            'postgres': 'sql',
            'javascript': 'javascript',
            'js': 'javascript',
            'react.js': 'react',
            'aws': 'aws',
            'amazon web services': 'aws',
            'azure': 'azure',
            'microsoft azure': 'azure',
            'gcp': 'gcp',
            'google cloud platform': 'gcp',
            'kubernetes': 'kubernetes',
            'k8s': 'kubernetes'
        }
        
        # Split into lines for section detection
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section type
            if any(keyword in line_lower for keyword in ['required:', 'requirements:', 'must have:', 'required skills:', 'qualifications:']):
                current_section = 'required'
            elif any(keyword in line_lower for keyword in ['preferred:', 'nice to have:', 'bonus:', 'preferred skills:', 'pluses:']):
                current_section = 'preferred'
            elif line_lower in ['', '---', '___']:
                current_section = None
            
            # Extract skills from current section
            if current_section:
                for skill in all_skills:
                    pattern = r'(^|\W)' + re.escape(skill) + r'($|\W)'
                    if re.search(pattern, line_lower):
                        canonical_skill = skill_cleanup.get(skill, skill)
                        if current_section == 'required':
                            required_skills.add(canonical_skill)
                        elif current_section == 'preferred':
                            preferred_skills.add(canonical_skill)
        
        # Also search entire text for skills with context
        for skill in all_skills:
            pattern = r'(^|\W)' + re.escape(skill) + r'($|\W)'
            if re.search(pattern, text_lower):
                canonical_skill = skill_cleanup.get(skill, skill)
                
                # Check context around the skill
                skill_pos = text_lower.find(skill)
                if skill_pos != -1:
                    # Get context around the skill
                    start = max(0, skill_pos - 50)
                    end = min(len(text_lower), skill_pos + len(skill) + 50)
                    context = text_lower[start:end]
                    
                    # Determine if required or preferred based on context
                    if any(word in context for word in ['required', 'must', 'need', 'essential', 'requirement']):
                        required_skills.add(canonical_skill)
                    elif any(word in context for word in ['preferred', 'nice', 'bonus', 'plus', 'desired']):
                        preferred_skills.add(canonical_skill)
                    else:
                        # Default to required if no context
                        required_skills.add(canonical_skill)
        
        # Remove any preferred skills that are also in required
        preferred_skills = preferred_skills - required_skills
        
        jd_data['required_skills'] = sorted(list(required_skills))
        jd_data['preferred_skills'] = sorted(list(preferred_skills))
        
        return jd_data