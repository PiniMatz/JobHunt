import os
import sys
from database import init_db, update_settings, get_settings, get_jobs_with_matches, add_job, save_match_result
from matching_agent import analyze_job_match
from scraper import fetch_mock_jobs

def run_test():
    print("Initializing Database...")
    init_db()
    
    # Define a sample CV
    sample_cv = """
    # PINI PM
    **Location**: Netanya, Israel
    **Professional Summary**: 
    Highly technical Product Manager with 5+ years of experience specializing in Data Platform, Analytics, and cloud infrastructure. Proven history of collaborating with developers, managing APIs, and creating data pipelines.
    
    **Skills**:
    - **Product Management**: Roadmap, PRD writing, Agile/Scrum, User Stories, A/B Testing.
    - **Data**: SQL (Snowflake/BigQuery), Python, ETL/ELT pipelines, BI (Tableau), Machine Learning models.
    - **Tech**: REST APIs, Docker, Kubernetes, AWS infrastructure.
    
    **Professional Experience**:
    - **Technical PM** at BigDataCorp (2023 - Present): Managed the central data API serving 10M+ daily requests. Built new telemetry pipeline in Python/SQL.
    - **Product Owner** at CloudScale (2021 - 2023): Designed developer-facing dashboard and API integrations.
    """
    
    print("Updating settings with sample CV and mock API key...")
    update_settings(cv_markdown=sample_cv, api_key="MOCK_API_KEY", locations=["Netanya"], threshold=70)
    
    settings = get_settings()
    print(f"Updated Settings: {settings}")
    
    # Retrieve mock jobs
    print("\nFetching mock jobs for Netanya...")
    jobs = fetch_mock_jobs(["Netanya"])
    print(f"Found {len(jobs)} mock jobs.")
    
    # Run mock matching for the first job
    if jobs:
        test_job = jobs[0]
        print(f"\nAnalyzing Match for Job: '{test_job['title']}' at {test_job['company']}")
        
        # Call matching agent (since API key is MOCK_API_KEY, it will return a simulated match)
        match_result = analyze_job_match(
            cv_markdown=sample_cv,
            job_title=test_job['title'],
            job_description=test_job['description'],
            api_key=settings["api_key"]
        )
        
        print("\nMatch Result:")
        print(f"Overall Score: {match_result['overall_score']}")
        print(f"Tech Score: {match_result['tech_score']}")
        print(f"Data Score: {match_result['data_score']}")
        print(f"PM Score: {match_result['pm_score']}")
        print(f"Fit Score: {match_result['fit_score']}")
        print(f"Pros: {match_result['pros']}")
        print(f"Cons: {match_result['cons']}")
        print(f"Red Flags: {match_result['red_flags']}")
        print(f"Explanation: {match_result['explanation']}")
        
        # Save to database
        job_id = add_job(
            title=test_job['title'],
            company=test_job['company'],
            location=test_job['location'],
            description=test_job['description'],
            url=test_job['url']
        )
        
        save_match_result(
            job_id=job_id,
            overall_score=match_result['overall_score'],
            tech_score=match_result['tech_score'],
            data_score=match_result['data_score'],
            pm_score=match_result['pm_score'],
            fit_score=match_result['fit_score'],
            pros=match_result['pros'],
            cons=match_result['cons'],
            red_flags=match_result['red_flags']
        )
        print(f"\nSaved job & match to database. Job ID: {job_id}")
        
        all_jobs = get_jobs_with_matches()
        print(f"Database contains {len(all_jobs)} jobs.")
        print("Test run completed successfully!")

if __name__ == "__main__":
    run_test()
