"""
Smart Resume-Job Matcher - AI Backend Components
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Professional Development Team"

# Export main classes for easy importing
from .document_parser import DocumentParser
from .matcher import MatchingEngine, ResumeJobMatcher
from .embedding_generator import EmbeddingGenerator
from .ai_explainer import AIExplainer
from .utils import save_results, load_results, convert_numpy_types

__all__ = [
    'DocumentParser',
    'MatchingEngine',
    'ResumeJobMatcher',
    'EmbeddingGenerator',
    'AIExplainer',
    'save_results',
    'load_results',
    'convert_numpy_types'
]