import streamlit as st
import pandas as pd
import numpy as np
from document_parser import DocumentParser
from embedding_generator import EmbeddingManager
from matching_engine import MatchingEngine
from ai_explainer import AIExplainer
import tempfile
import os

# Initialize components
@st.cache_resource
def load_services():
    return {
        'processor': DocumentProcessor(),
        'embedder': EmbeddingManager(),
        'matcher': MatchingEngine(),
        'explainer': AIExplainer(use_ollama=True)
    }

def main():
    st.set_page_config(
        page_title="Smart Resume & Job Matcher",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Smart Resume & Job Matcher")
    st.markdown("""
    An AI-powered system that uses semantic search and embeddings to match 
    resumes with job descriptions based on contextual understanding.
    """)
    
    # Initialize services
    services = load_services()
    
    # Sidebar for file uploads
    with st.sidebar:
        st.header("📂 Upload Documents")
        
        # Resume upload
        resume_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key='resume'
        )
        
        # Job description upload
        job_file = st.file_uploader(
            "Upload Job Description (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key='job'
        )
        
        # Alternative: Text input for job description
        st.header("OR")
        job_text = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste job description here..."
        )
        
        # Process button
        process_btn = st.button("🚀 Analyze Match", type="primary")
    
    # Main content area
    col1, col2 = st.columns(2)
    
    if process_btn and (resume_file or job_file or job_text):
        with st.spinner("Processing documents..."):
            # Process resume
            resume_text = ""
            if resume_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(resume_file.read())
                    resume_text = services['processor'].extract_text_from_pdf(tmp.name)
                os.unlink(tmp.name)
            
            # Process job description
            job_text_input = ""
            if job_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(job_file.read())
                    job_text_input = services['processor'].extract_text_from_pdf(tmp.name)
                os.unlink(tmp.name)
            elif job_text:
                job_text_input = job_text
            
            if resume_text and job_text_input:
                # Parse documents
                resume_data = services['processor'].parse_resume(resume_text)
                job_data = services['processor'].parse_job_description(job_text_input)
                
                # Create embeddings
                resume_embedding = services['embedder'].create_embeddings([resume_text])[0]
                job_embedding = services['embedder'].create_embeddings([job_text_input])[0]
                
                # Calculate semantic similarity
                semantic_score = services['matcher'].semantic_similarity(
                    resume_embedding, job_embedding
                )
                
                # Calculate match score
                match_result = services['matcher'].calculate_overall_match(
                    resume_data, job_data, semantic_score
                )
                
                # Display results
                with col1:
                    st.header("📊 Match Analysis")
                    
                    # Overall score gauge
                    score = match_result['overall_score']
                    st.metric("Overall Match Score", f"{score:.1f}%")
                    
                    # Progress bar for score
                    st.progress(score/100)
                    
                    # Display scores
                    st.subheader("Detailed Scores")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Skills Match", f"{match_result['skill_score']:.1f}%")
                    with cols[1]:
                        st.metric("Context Match", f"{match_result['semantic_score']:.1f}%")
                    with cols[2]:
                        st.metric("Required Skills Met", 
                                 f"{match_result['skill_details']['required_matches']}/{len(job_data['required_skills'])}")
                
                with col2:
                    st.header("🔍 Extracted Information")
                    
                    # Skills comparison
                    st.subheader("Skills Analysis")
                    skills_col1, skills_col2 = st.columns(2)
                    
                    with skills_col1:
                        st.write("**Resume Skills:**")
                        for skill in resume_data['skills'][:10]:
                            st.write(f"✅ {skill}")
                    
                    with skills_col2:
                        st.write("**Job Requirements:**")
                        for skill in job_data['required_skills'][:10]:
                            st.write(f"🎯 {skill}")
                
                # AI Explanation
                st.header("🤖 AI Match Explanation")
                with st.spinner("Generating AI explanation..."):
                    explanation = services['explainer'].generate_match_explanation(
                        resume_data, job_data, match_result
                    )
                    st.write(explanation)
                
                # Improvement suggestions
                with st.expander("💡 Improvement Suggestions"):
                    suggestions = services['explainer'].generate_improvement_suggestions(
                        resume_data, job_data
                    )
                    if isinstance(suggestions, str):
                        st.write(suggestions)
                    else:
                        for suggestion in suggestions:
                            st.write(f"- {suggestion}")
                
                # Show raw data (optional)
                with st.expander("📁 View Raw Data"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.json(resume_data)
                    with col2:
                        st.json(job_data)
    
    else:
        # Show welcome/instructions
        st.info("👈 Upload a resume and job description to get started!")
        
        # Show sample workflow
        with st.expander("📋 How it works"):
            st.markdown("""
            1. **Upload your resume** (PDF, DOCX, or TXT)
            2. **Upload or paste a job description**
            3. **Click 'Analyze Match'**
            
            The system will:
            - Extract skills, education, and experience
            - Create semantic embeddings
            - Calculate match scores
            - Generate AI-powered explanations
            - Provide improvement suggestions
            """)
        
        # Show sample output
        st.subheader("Example Output")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Match Score", "85%", "Excellent")
        with col2:
            st.metric("Skills Match", "92%", "+5%")
        with col3:
            st.metric("Missing Skills", "2", "Out of 15")

if __name__ == "__main__":
    main()