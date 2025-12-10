"""
Core Matching Engine for Smart Resume-Job Matcher
Professional AI-powered matching system using embeddings and semantic search
Author: Professional Development Team
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Core matching engine that calculates compatibility scores between
    resumes and job descriptions using multiple weighted factors.
    
    Features:
    - Semantic similarity using embeddings
    - Skill matching with required/preferred differentiation
    - Experience level matching with diminishing returns
    - Education hierarchy matching
    - Configurable weight system
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the matching engine with configurable weights.
        
        Args:
            weights (Dict[str, float], optional): Custom weights for scoring components.
                Defaults to: {
                    'required_skills': 0.35,
                    'preferred_skills': 0.20,
                    'experience': 0.25,
                    'education': 0.15,
                    'semantic': 0.05
                }
        
        Raises:
            ValueError: If weights do not sum to 1.0
        """
        self.weights = weights or {
            'required_skills': 0.35,    # Most critical: Required skills match
            'preferred_skills': 0.20,   # Bonus for having preferred skills
            'experience': 0.25,         # Years of experience match
            'education': 0.15,          # Educational qualifications
            'semantic': 0.05            # Contextual/semantic similarity
        }
        
        # Validate weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight:.3f}")
        
        logger.info(f"MatchingEngine initialized with weights: {self.weights}")
    
    def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skill strings for consistent matching.
        
        Args:
            skills (List[str]): List of skill strings
            
        Returns:
            List[str]: Normalized, deduplicated skills in lowercase
        """
        if not skills:
            return []
        
        normalized_skills = set()
        for skill in skills:
            if isinstance(skill, str) and skill.strip():
                # Remove extra whitespace and convert to lowercase
                clean_skill = ' '.join(skill.strip().lower().split())
                normalized_skills.add(clean_skill)
        
        return sorted(list(normalized_skills))
    
    def calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (np.ndarray): First vector
            vec2 (np.ndarray): Second vector
            
        Returns:
            float: Cosine similarity score between 0 and 1
        """
        if vec1 is None or vec2 is None:
            return 0.0
        
        try:
            # Ensure vectors are 1D
            vec1_flat = vec1.flatten().astype(np.float32)
            vec2_flat = vec2.flatten().astype(np.float32)
            
            # Handle dimension mismatch
            if len(vec1_flat) != len(vec2_flat):
                min_len = min(len(vec1_flat), len(vec2_flat))
                vec1_flat = vec1_flat[:min_len]
                vec2_flat = vec2_flat[:min_len]
            
            # Calculate dot product and norms
            dot_product = np.dot(vec1_flat, vec2_flat)
            norm1 = np.linalg.norm(vec1_flat)
            norm2 = np.linalg.norm(vec2_flat)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(max(similarity, 0.0))  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def calculate_skill_score(self, resume_skills: List[str], 
                            job_required_skills: List[str], 
                            job_preferred_skills: List[str]) -> Dict[str, Any]:
        """
        Calculate detailed skill matching score with breakdown.
        
        Args:
            resume_skills (List[str]): Skills from resume
            job_required_skills (List[str]): Required skills from job
            job_preferred_skills (List[str]): Preferred skills from job
            
        Returns:
            Dict[str, Any]: Detailed skill matching results
        """
        # Normalize all skills
        resume_skills_norm = self.normalize_skills(resume_skills)
        required_skills_norm = self.normalize_skills(job_required_skills)
        preferred_skills_norm = self.normalize_skills(job_preferred_skills)
        
        # Convert to sets for efficient operations
        resume_set = set(resume_skills_norm)
        required_set = set(required_skills_norm)
        preferred_set = set(preferred_skills_norm)
        
        # Calculate matches
        required_matches = list(resume_set.intersection(required_set))
        preferred_matches = list(resume_set.intersection(preferred_set))
        missing_required = list(required_set - resume_set)
        missing_preferred = list(preferred_set - resume_set)
        
        # Calculate coverage scores
        required_coverage = (len(required_matches) / len(required_set) 
                           if required_set else 1.0)
        preferred_coverage = (len(preferred_matches) / len(preferred_set) 
                            if preferred_set else 1.0)
        
        # Calculate overall skill score (required skills are critical)
        if required_set:
            skill_score = (required_coverage * 0.7) + (preferred_coverage * 0.3)
        else:
            skill_score = preferred_coverage  # If no required skills
        
        return {
            'score': skill_score * 100,  # Convert to percentage
            'required_matches': required_matches,
            'preferred_matches': preferred_matches,
            'missing_required': missing_required,
            'missing_preferred': missing_preferred,
            'required_coverage': f"{len(required_matches)}/{len(required_set)}",
            'preferred_coverage': f"{len(preferred_matches)}/{len(preferred_set)}",
            'resume_skill_count': len(resume_skills_norm),
            'required_skill_count': len(required_set),
            'preferred_skill_count': len(preferred_set)
        }
    
    def calculate_experience_score(self, resume_years: float, 
                                 job_required_years: float) -> float:
        """
        Calculate experience match score with diminishing returns for over-qualification.
        
        Args:
            resume_years (float): Years of experience from resume
            job_required_years (float): Required years from job description
            
        Returns:
            float: Experience match score (0.0 to 1.3)
        """
        if job_required_years <= 0:
            return 1.0  # No experience requirement specified
        
        if resume_years >= job_required_years:
            # Candidate meets or exceeds requirement
            excess_years = resume_years - job_required_years
            # Diminishing returns: max 30% bonus for excess experience
            bonus = min(excess_years * 0.1, 0.3)
            return 1.0 + bonus
        else:
            # Candidate has less experience than required
            ratio = resume_years / job_required_years
            # Penalize more severely for severe under-qualification
            if ratio < 0.5:
                return ratio * 0.8
            else:
                return ratio
    
    def calculate_education_score(self, resume_education: List[str], 
                                job_education_required: List[str]) -> float:
        """
        Calculate education match score considering degree hierarchy.
        
        Args:
            resume_education (List[str]): Education details from resume
            job_education_required (List[str]): Required education from job
            
        Returns:
            float: Education match score (0.0 to 1.0)
        """
        if not job_education_required:
            return 1.0  # No specific education requirement
        
        if not resume_education:
            return 0.0  # No education information provided
        
        # Education hierarchy (higher number = higher level)
        education_hierarchy = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'bs': 3,
            'ba': 3,
            'master': 4,
            'ms': 4,
            'ma': 4,
            'mba': 4,
            'phd': 5,
            'doctorate': 5,
            'ph.d': 5
        }
        
        # Find highest education level in resume
        resume_levels = []
        for edu in resume_education:
            edu_lower = edu.lower()
            for level, value in education_hierarchy.items():
                if level in edu_lower:
                    resume_levels.append(value)
                    break
        
        if not resume_levels:
            return 0.3  # Some credit for having education section
        
        max_resume_level = max(resume_levels)
        
        # Check against job requirements
        for req_edu in job_education_required:
            req_lower = req_edu.lower()
            for level, value in education_hierarchy.items():
                if level in req_lower:
                    if max_resume_level >= value:
                        return 1.0  # Meets or exceeds requirement
                    else:
                        # Partial credit based on proximity to requirement
                        proximity_score = max_resume_level / value
                        return max(0.3, proximity_score)
        
        return 0.5  # Default partial credit if no specific match
    
    def match(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], 
             resume_embedding: Optional[np.ndarray] = None, 
             job_embedding: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job.
        
        Args:
            resume_data (Dict[str, Any]): Parsed resume data
            job_data (Dict[str, Any]): Parsed job description data
            resume_embedding (np.ndarray, optional): Resume embedding vector
            job_embedding (np.ndarray, optional): Job description embedding vector
            
        Returns:
            Dict[str, Any]: Complete match results with detailed breakdown
        """
        logger.info("Calculating match score between resume and job")
        
        # Skill matching
        skill_result = self.calculate_skill_score(
            resume_skills=resume_data.get('skills', []),
            job_required_skills=job_data.get('required_skills', []),
            job_preferred_skills=job_data.get('preferred_skills', [])
        )
        
        # Experience matching
        experience_score = self.calculate_experience_score(
            resume_years=resume_data.get('experience_years', 0),
            job_required_years=job_data.get('experience_required', 0)
        )
        
        # Education matching
        education_score = self.calculate_education_score(
            resume_education=resume_data.get('education', []),
            job_education_required=job_data.get('education_required', [])
        )
        
        # Semantic similarity (if embeddings available)
        semantic_score = 0.0
        if resume_embedding is not None and job_embedding is not None:
            semantic_score = self.calculate_cosine_similarity(
                resume_embedding, 
                job_embedding
            )
        
        # Calculate weighted overall score
        weighted_score = (
            self.weights['required_skills'] * (skill_result['score'] / 100) +
            self.weights['preferred_skills'] * (len(skill_result['preferred_matches']) / 
                                              max(len(job_data.get('preferred_skills', [])), 1)) +
            self.weights['experience'] * min(experience_score, 1.3) +
            self.weights['education'] * education_score +
            self.weights['semantic'] * semantic_score
        )
        
        # Convert to percentage and cap at 100%
        overall_score = min(weighted_score * 100, 100)
        
        # Prepare comprehensive results
        match_result = {
            'overall_score': float(overall_score),
            'skill_score': float(skill_result['score']),
            'experience_score': float(min(experience_score, 1.3) * 100),
            'education_score': float(education_score * 100),
            'semantic_score': float(semantic_score * 100),
            'skill_details': skill_result,
            'weighted_components': {
                'required_skills': float(self.weights['required_skills'] * 
                                       (skill_result['score'] / 100) * 100),
                'preferred_skills': float(self.weights['preferred_skills'] * 
                                        (len(skill_result['preferred_matches']) / 
                                         max(len(job_data.get('preferred_skills', [])), 1)) * 100),
                'experience': float(self.weights['experience'] * 
                                  min(experience_score, 1.3) * 100),
                'education': float(self.weights['education'] * education_score * 100),
                'semantic': float(self.weights['semantic'] * semantic_score * 100)
            },
            'match_summary': {
                'skills': f"{len(skill_result['required_matches'])}/{len(job_data.get('required_skills', []))} required skills matched",
                'experience': f"{resume_data.get('experience_years', 0)}/{job_data.get('experience_required', 0)} years",
                'education': "Meets requirement" if education_score >= 0.8 else 
                           ("Partial match" if education_score >= 0.5 else "Below requirement"),
                'semantic_similarity': f"{semantic_score:.1%}"
            }
        }
        
        logger.info(f"Match calculation complete: {overall_score:.1f}%")
        return match_result
    
    def batch_match(self, resumes_data: List[Dict[str, Any]], 
                   job_data: Dict[str, Any],
                   resume_embeddings: Optional[List[np.ndarray]] = None) -> List[Dict[str, Any]]:
        """
        Match multiple resumes against a single job description.
        
        Args:
            resumes_data (List[Dict[str, Any]]): List of parsed resume data
            job_data (Dict[str, Any]): Parsed job description data
            resume_embeddings (List[np.ndarray], optional): List of resume embeddings
            
        Returns:
            List[Dict[str, Any]]: List of match results sorted by score (descending)
        """
        logger.info(f"Starting batch matching for {len(resumes_data)} resumes")
        
        results = []
        
        for i, resume_data in enumerate(resumes_data):
            try:
                resume_embedding = (resume_embeddings[i] 
                                  if resume_embeddings and i < len(resume_embeddings) 
                                  else None)
                
                match_result = self.match(
                    resume_data=resume_data,
                    job_data=job_data,
                    resume_embedding=resume_embedding,
                    job_embedding=None  # Job embedding would be same for all
                )
                
                results.append({
                    'resume_index': i,
                    'match_score': match_result['overall_score'],
                    'details': match_result
                })
                
                logger.debug(f"Resume {i+1}/{len(resumes_data)}: {match_result['overall_score']:.1f}%")
                
            except Exception as e:
                logger.error(f"Failed to match resume {i}: {e}")
                results.append({
                    'resume_index': i,
                    'match_score': 0.0,
                    'error': str(e)
                })
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        logger.info(f"Batch matching completed: {len(results)} results processed")
        return results


# Create alias for backward compatibility
ResumeJobMatcher = MatchingEngine