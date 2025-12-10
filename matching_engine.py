import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class MatchingEngine:
    def __init__(self):
        self.skill_weights = {
            'required_skills': 0.4,
            'preferred_skills': 0.2,
            'experience': 0.2,
            'education': 0.1,
            'industry_keywords': 0.1
        }
    
    def semantic_similarity(self, resume_embedding: np.ndarray, 
                          job_embedding: np.ndarray) -> float:
        """Calculate semantic similarity between embeddings"""
        similarity = cosine_similarity(
            resume_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]
        return float(similarity)
    
    def skill_match_score(self, resume_skills: List[str], 
                         job_required: List[str], 
                         job_preferred: List[str]) -> Dict:
        """Calculate skill-based matching score"""
        resume_skills_lower = [s.lower() for s in resume_skills]
        job_required_lower = [j.lower() for j in job_required]
        job_preferred_lower = [j.lower() for j in job_preferred]
        
        # Calculate matches
        required_matches = len(set(resume_skills_lower) & set(job_required_lower))
        preferred_matches = len(set(resume_skills_lower) & set(job_preferred_lower))
        
        # Calculate scores
        required_score = (required_matches / max(len(job_required_lower), 1)) * 100
        preferred_score = (preferred_matches / max(len(job_preferred_lower), 1)) * 50
        
        total_skill_score = min(required_score + preferred_score, 100)
        
        return {
            'score': total_skill_score,
            'required_matches': required_matches,
            'preferred_matches': preferred_matches,
            'missing_required': list(set(job_required_lower) - set(resume_skills_lower))
        }
    
    def calculate_overall_match(self, resume_data: Dict, 
                              job_data: Dict, 
                              semantic_score: float) -> Dict:
        """Calculate overall match score with weighted components"""
        
        # Skill matching
        skill_result = self.skill_match_score(
            resume_data['skills'],
            job_data['required_skills'],
            job_data['preferred_skills']
        )
        
        # Calculate weighted score
        weighted_score = (
            self.skill_weights['required_skills'] * skill_result['score']/100 +
            self.skill_weights['preferred_skills'] * (skill_result['preferred_matches']/max(len(job_data['preferred_skills']), 1)) +
            self.skill_weights['experience'] * 0.8 +  # Simplified experience matching
            self.skill_weights['education'] * 0.9 +   # Simplified education matching
            self.skill_weights['industry_keywords'] * semantic_score
        ) * 100
        
        return {
            'overall_score': min(weighted_score, 100),
            'semantic_score': semantic_score * 100,
            'skill_score': skill_result['score'],
            'skill_details': skill_result,
            'match_breakdown': {
                'skills': skill_result['score'],
                'semantic': semantic_score * 100
            }
        }