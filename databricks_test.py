import pandas as pd

# Create realistic matching results (no JSON needed)
matches_df = pd.DataFrame({
    'candidate': ['John Doe AI Engineer', 'Jane Smith Data Scientist', 'Mike Chen Quant Analyst'],
    'job_title': ['AI Engineering Intern - BIT Capital', 'Data Engineer - Finance', 'Investment Analyst'],
    'match_score': [0.92, 0.87, 0.91],
    'skills_matched': ['Python,LLM,Databricks,APIs', 'SQL,Pipelines,Snowflake,AWS', 'Python,Finance,ML,SQL'],
    'reason': ['Perfect BIT Capital AI Intern fit', 'Strong data pipeline skills', 'Quant + tech background']
})

# Save as Delta format for Databricks
matches_df.to_parquet('matches_delta.parquet', index=False)
print("✅ Delta file created!")
print(matches_df)
