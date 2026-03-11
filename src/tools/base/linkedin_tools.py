import os
import requests
from src.utils import invoke_llm

def extract_linkedin_url_base(search_results):
    """
    Extracts the LinkedIn URL from the search results.
    """
    for result in search_results:
        if 'linkedin.com/in' in result['link']:
            return result['link']
    return ""


def extract_linkedin_url(search_results):
    EXTRACT_LINKEDIN_URL_PROMPT = """
    **Role:**  
    You are an expert in extracting LinkedIn URLs from Google search results, specializing in finding the correct personal LinkedIn URL.

    **Objective:**  
    From the provided search results, find the LinkedIn URL of a specific person working at a specific company.

    **Instructions:**  
    1. Output **only** the correct LinkedIn URL if found, nothing else.  
    2. If no valid URL exists, output **only** an empty string.  
    3. Only consider URLs with `"/in"`. Ignore those with `"/posts"` or `"/company"`.  
    """
    
    result = invoke_llm(
        system_prompt=EXTRACT_LINKEDIN_URL_PROMPT,
        user_message=str(search_results),
        model="gpt-4o-mini"
    )
    return result
    
    
def scrape_linkedin(linkedin_url, is_company=False):
    """
    Scrapes LinkedIn profile data based on the provided LinkedIn URL.
    
    @param linkedin_url: The LinkedIn URL to scrape.
    @param is_company: Boolean indicating whether to scrape a company profile or a person profile.
    @return: The scraped LinkedIn profile data.
    """
    if is_company:
        url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-company-by-linkedinurl"
        querystring = {"linkedin_url": linkedin_url}
    else:
        # 개인 프로필: /get-linkedin-profile → /enrich-lead 로 엔드포인트 변경됨 (2025)
        url = "https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead"
        querystring = {
            "linkedin_url": linkedin_url,
            "include_skills": "false",
            "include_certifications": "false",
            "include_publications": "false",
            "include_honors": "false",
            "include_volunteers": "false",
            "include_projects": "false",
            "include_patents": "false",
            "include_courses": "false",
            "include_organizations": "false",
            "include_profile_status": "false",
            "include_company_public_url": "false",
        }
    headers = {
      "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
      "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"LinkedIn URL used: {linkedin_url}")
        print(f"Response body: {response.text}")
        return {}