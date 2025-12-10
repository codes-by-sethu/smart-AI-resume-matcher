"""
AI Explanation Generator
"""
from typing import Dict, List
from datetime import datetime

class AIExplainer:
    """Generate human-readable explanations for matches"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load explanation templates"""
        return {
            'excellent': [
                "🎯 **EXCELLENT MATCH** - This candidate strongly aligns with all job requirements.",
                "**Key Strengths:** Complete skill overlap, exceeds experience requirements.",
                "**Recommendation:** Highly recommended for immediate interview consideration."
            ],
            'good': [
                "✅ **STRONG MATCH** - Candidate meets most requirements with excellent core skills.",
                "**Strengths:** Strong foundation in key required areas.",
                "**Recommendation:** Strong candidate worth interviewing."
            ],
            'fair': [
                "⚠️ **GOOD MATCH** - Candidate has relevant experience with some skill gaps.",
                "**Strengths:** Has most required skills and meets experience requirements.",
                "**Gaps:** Missing some preferred skills.",
                "**Recommendation:** Consider if other candidates are unavailable."
            ],
            'poor': [
                "❌ **POOR MATCH** - Significant gaps between candidate and job requirements.",
                "**Issues:** Missing critical required skills or insufficient experience.",
                "**Recommendation:** Not recommended for this role."
            ]
        }
    
    def generate_match_explanation(self, resume_data: Dict, 
                                 job_data: Dict, 
                                 match_result: Dict) -> str:
        """Generate explanation for match"""
        
        overall_score = match_result['overall_score']
        
        # Determine match level
        if overall_score >= 90:
            match_level = 'excellent'
        elif overall_score >= 80:
            match_level = 'good'
        elif overall_score >= 70:
            match_level = 'fair'
        else:
            match_level = 'poor'
        
        # Build explanation
        explanation = []
        explanation.extend(self.templates[match_level])
        
        # Add skill analysis
        skill_details = match_result.get('skill_details', {})
        required_matches = skill_details.get('required_matches', [])
        missing_required = skill_details.get('missing_required', [])
        
        explanation.append(f"\n**📊 SKILL ANALYSIS**")
        explanation.append(f"- **Required Skills Matched ({len(required_matches)}/{len(job_data['required_skills'])}):**")
        if required_matches:
            for skill in required_matches[:5]:
                explanation.append(f"  ✓ {skill}")
        
        if missing_required:
            explanation.append(f"- **Missing Required Skills ({len(missing_required)}):**")
            for skill in missing_required[:3]:
                explanation.append(f"  ✗ {skill}")
        
        # Add experience analysis
        exp_years = resume_data.get('experience_years', 0)
        exp_required = job_data.get('experience_required', 0)
        
        explanation.append(f"\n**⏳ EXPERIENCE ANALYSIS**")
        if exp_years >= exp_required:
            explanation.append(f"✓ Exceeds requirement: {exp_years} years (vs {exp_required} required)")
        else:
            explanation.append(f"⚠️  Below requirement: {exp_years} years (vs {exp_required} required)")
        
        # Add specific recommendations
        explanation.append(f"\n**💡 NEXT STEPS**")
        
        if match_level == 'excellent':
            explanation.append("1. Schedule interview immediately")
            explanation.append("2. Discuss specific projects and achievements")
            explanation.append("3. Consider technical assessment for validation")
        elif match_level == 'good':
            explanation.append("1. Schedule screening interview")
            explanation.append("2. Verify missing preferred skills")
            explanation.append("3. Discuss career goals and growth potential")
        elif match_level == 'fair':
            explanation.append("1. Conduct phone screening first")
            explanation.append("2. Assess willingness to learn missing skills")
            explanation.append("3. Compare with other candidates")
        else:
            explanation.append("1. Consider for different role")
            explanation.append("2. Keep in talent pool for future")
            explanation.append("3. Provide constructive feedback")
        
        explanation.append(f"\n*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        return "\n".join(explanation)