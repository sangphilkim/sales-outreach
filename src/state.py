from pydantic import BaseModel, Field
from typing import List, Annotated
from typing_extensions import TypedDict
def reports_reducer(existing: list, update):
    if update is None:
        return []              # None이면 초기화 (새 lead 시작 시)
    return existing + update   # 아니면 기존처럼 누적

class SocialMediaLinks(BaseModel):
    blog: str = ""
    facebook: str = ""
    twitter: str = ""
    youtube: str = ""
    # Can add other platform
    
class Report(BaseModel):
    title: str = ""
    content: str = ""
    is_markdown: bool = False

# Define the base data needed about the lead
class LeadData(BaseModel):
    id: str = Field(..., description="The unique identifier for the lead being processed")
    name: str = Field(..., description="The full name of the lead")
    address: str = Field(..., description="The address of the lead")
    email: str = Field(..., description="The email address of the lead")
    phone: str = Field(..., description="The phone number of the lead")
    profile: str = Field(..., description="The lead profile summary from LinkedIn data")

class CompanyData(BaseModel):
    name: str = ""
    profile: str = ""
    website: str = ""
    social_media_links: SocialMediaLinks = SocialMediaLinks()
    
class GraphInputState(TypedDict):
    leads_ids: List[str]

class GraphState(TypedDict):
    leads_ids: List[str]
    leads_data: List[dict]
    current_lead: LeadData
    lead_score: str = ""
    company_data: CompanyData
    reports: Annotated[list[Report], reports_reducer]
    reports_folder_link: str
    custom_outreach_report_link: str
    # personalized_email: str  # reports 리스트 방식으로 변경되며 미사용 (dead code). 향후 직접 state 저장 방식으로 전환 시 재활성화
    # interview_script: str    # reports 리스트 방식으로 변경되며 미사용 (dead code). 향후 직접 state 저장 방식으로 전환 시 재활성화
    number_leads: int