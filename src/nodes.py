import re
from colorama import Fore, Style
from langsmith import Client as LangSmithClient
from .tools.base.markdown_scraper_tool import scrape_website_to_markdown
from .tools.base.search_tools import get_recent_news
from .tools.base.gmail_tools import GmailTools
from .tools.google_docs_tools import GoogleDocsManager
from .tools.lead_research import research_lead_on_linkedin
from .tools.company_research import research_lead_company, generate_company_profile
from .tools.youtube_tools import get_youtube_stats
from .tools.rag_tool import fetch_similar_case_study
from .prompts import *
from .state import LeadData, CompanyData, Report, GraphInputState, GraphState
from .structured_outputs import WebsiteData, EmailResponse
from .utils import invoke_llm, get_report, get_current_date, save_reports_locally

# Enable or disable sending emails directly using GMAIL
# Should be confident about the quality of the email
SEND_EMAIL_DIRECTLY = False
# Enable or disable saving emails to Google Docs
# By defauly all reports are save locally in `reports` folder
SAVE_TO_GOOGLE_DOCS = False

class OutReachAutomationNodes:
    def __init__(self, loader):
        self.lead_loader = loader
        self.docs_manager = GoogleDocsManager()

    def get_new_leads(self, state: GraphInputState):
        print(Fore.YELLOW + "----- Fetching new leads -----\n" + Style.RESET_ALL)
        
        # Fetch new leads using the provided loader
        # leads_ids가 있으면 해당 ID만, 없으면 모든 NEW 리드 조회
        leads_ids = state.get("leads_ids", [])
        raw_leads = self.lead_loader.fetch_records(
            lead_ids=leads_ids if leads_ids else None
        )
        
        # Structure the leads
        leads = [
            LeadData(
                id=lead["id"],
                name=f'{lead.get("First Name", "")} {lead.get("Last Name", "")}',
                email=lead.get("Email", ""),
                phone=lead.get("Phone", ""),
                address=lead.get("Address", ""),
                profile="" # will be constructed
            )
            for lead in raw_leads
        ]
        
        print(Fore.YELLOW + f"----- Fetched {len(leads)} leads -----\n" + Style.RESET_ALL)
        return {"leads_data": leads, "number_leads": len(leads)}
    
    @staticmethod
    def check_for_remaining_leads(state: GraphState):
        """Checks for remaining leads and updates lead_data in the state."""
        print(Fore.YELLOW + "----- Checking for remaining leads -----\n" + Style.RESET_ALL)
        
        current_lead = None
        if state["leads_data"]:
            current_lead = state["leads_data"].pop()
        return {"current_lead": current_lead}

    @staticmethod
    def check_if_there_more_leads(state: GraphState):
        # Number of leads remaining
        num_leads = state["number_leads"]
        if num_leads > 0:
            print(Fore.YELLOW + f"----- Found {num_leads} more leads -----\n" + Style.RESET_ALL)
            return "Found leads"
        else:
            print(Fore.GREEN + "----- Finished, No more leads -----\n" + Style.RESET_ALL)
            return "No more leads"

    def fetch_linkedin_profile_data(self, state: GraphState):
        print(Fore.YELLOW + "----- Searching Lead data on LinkedIn -----\n" + Style.RESET_ALL)
        lead_data = state["current_lead"]
        company_data = CompanyData()  # 새 lead 시작 시 company_data 초기화

        # Scrape lead linkedin profile
        try:
            result = research_lead_on_linkedin(lead_data.name, lead_data.email)

            if isinstance(result, str):
                # LinkedIn lookup failed, continue with available data
                print(Fore.RED + f"LinkedIn research failed: {result}" + Style.RESET_ALL)
                lead_data.profile = ""
            else:
                lead_profile, company_name, company_website, company_linkedin_url = result
                lead_data.profile = lead_profile

                # Research company on linkedin (URL 있을 때만 호출)
                if company_linkedin_url:
                    company_profile = research_lead_company(company_linkedin_url)
                else:
                    company_profile = {}

                # Update company name from LinkedIn data
                company_data.name = company_name
                company_data.website = company_website
                company_data.profile = str(company_profile)
        except Exception as e:
            print(Fore.RED + f"LinkedIn research error: {e}" + Style.RESET_ALL)
            lead_data.profile = ""

        # drive_folder_name: 공통 폴더명으로 사용하려 했으나 각 노드에서 직접 생성하는 방식으로 변경됨 (dead code)
        # self.drive_folder_name = f"{lead_data.name}_{company_data.name}"

        return {
            "current_lead": lead_data,
            "company_data": company_data,
            "reports": None,              # 새 lead 시작 시 reports 초기화
            "reports_folder_link": "",    # 새 lead 시작 시 링크 초기화
            "custom_outreach_report_link": "",  # 새 lead 시작 시 링크 초기화
        }
    
    def review_company_website(self, state: GraphState):
        print(Fore.YELLOW + "----- Scraping company website -----\n" + Style.RESET_ALL)
        lead_data = state.get("current_lead")
        company_data = state.get("company_data")
        
        company_website = company_data.website
        if company_website:
            try:
                # Scrape company website
                content = scrape_website_to_markdown(company_website)
                website_info = invoke_llm(
                    system_prompt=WEBSITE_ANALYSIS_PROMPT.format(main_url=company_website),
                    user_message=content,
                    model="gpt-4o-mini",
                    response_format=WebsiteData
                )

                # Extract all relevant links
                company_data.social_media_links.blog = website_info.blog_url
                company_data.social_media_links.facebook = website_info.facebook
                company_data.social_media_links.twitter = website_info.twitter
                company_data.social_media_links.youtube = website_info.youtube

                # Update company profile with website summary
                company_data.profile = generate_company_profile(company_data.profile, website_info.summary)
            except Exception as e:
                print(Fore.RED + f"Website scraping failed: {e}" + Style.RESET_ALL)
                 
        inputs = f"""
        # **Lead Profile:**

        {lead_data.profile}

        # **Company Information:**

        {company_data.profile}
        """
        
        # Generate general lead search report
        general_lead_search_report = invoke_llm(
            system_prompt=LEAD_SEARCH_REPORT_PROMPT,
            user_message=inputs,
            model="gpt-4o-mini"
        )
        
        lead_search_report = Report(
            title="General Lead Research Report",
            content=general_lead_search_report,
            is_markdown=True
        )
        
        return {
            "company_data": company_data,
            "reports": [lead_search_report]
        }
    
    @staticmethod
    def collect_company_information(state: GraphState):
        return {"reports": []}
    
    def analyze_blog_content(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing company main blog -----\n" + Style.RESET_ALL)

        blog_analysis_report = None

        # Check if company has a blog
        company_data = state["company_data"]
        blog_url = company_data.social_media_links.blog
        if blog_url:
            try:
                blog_content = scrape_website_to_markdown(blog_url)
                prompt = BLOG_ANALYSIS_PROMPT.format(company_name=company_data.name)
                blog_analysis_report = invoke_llm(
                    system_prompt=prompt,
                    user_message=blog_content,
                    model="gpt-4o-mini"
                )
                blog_analysis_report = Report(
                    title="Blog Analysis Report",
                    content=blog_analysis_report,
                    is_markdown=True
                )
            except Exception as e:
                print(Fore.RED + f"Blog scraping failed: {e}" + Style.RESET_ALL)

        reports = [r for r in [blog_analysis_report] if r is not None]
        return {"reports": reports}
    
    def analyze_social_media_content(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing company social media accounts -----\n" + Style.RESET_ALL)

        # Load states
        company_data = state["company_data"]

        # Get social media urls
        facebook_url = company_data.social_media_links.facebook
        twitter_url = company_data.social_media_links.twitter
        youtube_url = company_data.social_media_links.youtube

        youtube_analysis_report = None

        # Check If company has Youtube channel
        if youtube_url:
            try:
                youtube_data = get_youtube_stats(youtube_url)
                prompt = YOUTUBE_ANALYSIS_PROMPT.format(company_name=company_data.name)
                youtube_insight = invoke_llm(
                    system_prompt=prompt,
                    user_message=youtube_data,
                    model="gpt-4o-mini"
                )
                youtube_analysis_report = Report(
                    title="Youtube Analysis Report",
                    content=youtube_insight,
                    is_markdown=True
                )
            except Exception as e:
                print(Fore.RED + f"YouTube analysis failed: {e}" + Style.RESET_ALL)
                # youtube_analysis_report = None 유지 → 이후 필터링에서 제외

        # Check If company has Facebook account
        if facebook_url:
            # TODO Add Facebook analysis part
            pass

        # Check If company has Twitter account
        if twitter_url:
            # TODO Add Twitter analysis part
            pass

        reports = [r for r in [youtube_analysis_report] if r is not None]
        return {
            "company_data": company_data,
            "reports": reports
        }
    
    def analyze_recent_news(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing recent news about company -----\n" + Style.RESET_ALL)

        # Load states
        company_data = state["company_data"]

        # 회사명이 없으면 뉴스 검색 스킵
        if not company_data.name:
            print(Fore.YELLOW + "회사명 없음, 뉴스 검색 스킵" + Style.RESET_ALL)
            return {"reports": []}

        # Fetch recent news using serper API
        recent_news = get_recent_news(company=company_data.name)
        number_months = 6
        current_date = get_current_date()
        news_analysis_prompt = NEWS_ANALYSIS_PROMPT.format(
            company_name=company_data.name, 
            number_months=number_months, 
            date=current_date
        )
        
        # Craft news analysis prompt
        news_insight = invoke_llm(
            system_prompt=news_analysis_prompt,
            user_message=recent_news,
            model="gpt-4o-mini"
        )
        
        news_analysis_report = Report(
            title="News Analysis Report",
            content=news_insight,
            is_markdown=True
        )
        return {"reports": [news_analysis_report]}
    
    def generate_digital_presence_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Generate Digital presence analysis report -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        blog_analysis_report = get_report(reports, "Blog Analysis Report")
        facebook_analysis_report = get_report(reports, "Facebook Analysis Report")
        twitter_analysis_report = get_report(reports, "Twitter Analysis Report")
        youtube_analysis_report = get_report(reports, "Youtube Analysis Report")
        news_analysis_report = get_report(reports, "News Analysis Report")
        
        inputs = f"""
        # **Digital Presence Data:**
        ## **Blog Information:**

        {blog_analysis_report}
        
        ## **Facebook Information:**

        {facebook_analysis_report}
        
        ## **Twitter Information:**

        {twitter_analysis_report}

        ## **Youtube Information:**

        {youtube_analysis_report}

        # **Recent News:**

        {news_analysis_report}
        """
        
        prompt = DIGITAL_PRESENCE_REPORT_PROMPT.format(
            company_name=state["company_data"].name, date=get_current_date()
        )
        digital_presence_report = invoke_llm(
            system_prompt=prompt,
            user_message=inputs,
            model="gpt-4o-mini"
        )
        
        digital_presence_report = Report(
            title="Digital Presence Report",
            content=digital_presence_report,
            is_markdown=True
        )
        return {"reports": [digital_presence_report]}
    
    def generate_full_lead_research_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Generate global lead analysis report -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        general_lead_search_report = get_report(reports, "General Lead Research Report")
        digital_presence_report = get_report(reports, "Digital Presence Report")
        
        inputs = f"""
        # **Lead & company Information:**

        {general_lead_search_report}
        
        ---

        # **Digital Presence Information:**

        {digital_presence_report}
        """
        
        prompt = GLOBAL_LEAD_RESEARCH_REPORT_PROMPT.format(
            company_name=state["company_data"].name, date=get_current_date()
        )
        full_report = invoke_llm(
            system_prompt=prompt,
            user_message=inputs,
            model="gpt-4o-mini"
        )
        
        global_research_report = Report(
            title="Global Lead Analysis Report",
            content=full_report,
            is_markdown=True
        )
        return {"reports": [global_research_report]}
    
    @staticmethod
    def score_lead(state: GraphState):
        """
        Score the lead based on the company profile and open positions.

        @param state: The current state of the application.
        @return: Updated state with the lead score.
        """
        print(Fore.YELLOW + "----- Scoring lead -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        
        # Scoring lead
        lead_score = invoke_llm(
            system_prompt=SCORE_LEAD_PROMPT,
            user_message=global_research_report,
            model="gpt-4o"
        )
        # "FINAL SCORE: X.X" 형식에서 점수 추출 (CoT 출력 포함 시에도 안전)
        match = re.search(r'FINAL SCORE:\s*(\d+\.?\d*)', lead_score, re.IGNORECASE)
        if not match:
            # fallback: 형식이 없으면 마지막 숫자 추출
            match = re.search(r'(\d+\.?\d*)(?!.*\d)', lead_score.strip())

        final_score_str = match.group(1) if match else lead_score.strip()

        # LangSmith에 점수 메타데이터 기록
        try:
            final_score_float = float(final_score_str)
            company_name = state["company_data"].name if state.get("company_data") else "unknown"
            langsmith_client = LangSmithClient()
            langsmith_client.create_run(
                name="score_lead_result",
                run_type="chain",
                inputs={"company": company_name},
                outputs={
                    "final_score": final_score_float,
                    "qualified": final_score_float >= 6.0,
                    "raw_output": lead_score
                },
                tags=["scoring", "qualified" if final_score_float >= 6.0 else "not-qualified"]
            )
        except Exception:
            pass  # LangSmith 장애 시 에이전트 계속 실행

        return {"lead_score": final_score_str}

    # NOTE: 향후 프로그램 확장 시 활용 가능한 코드
    # 자격 여부를 state에 저장하여 update_CRM 등 하위 노드에서 참조할 때 사용
    # 활성화 시: state.py에 is_qualified: bool 필드 추가 필요
    #            graph.py에서 score_lead → is_lead_qualified → check_if_qualified 순서로 연결 필요
    #
    # @staticmethod
    # def is_lead_qualified(state: GraphState):
    #     """
    #     Check if the lead is qualified based on the lead score.
    #     Stores qualification result in state for use by downstream nodes (e.g. update_CRM).
    #
    #     @param state: The current state of the application.
    #     @return: Updated state with the qualification status.
    #     """
    #     print(Fore.YELLOW + "----- Checking if lead is qualified -----\n" + Style.RESET_ALL)
    #     try:
    #         match = re.search(r'\d+\.?\d*', str(state["lead_score"]))
    #         score = float(match.group()) if match else 0
    #         qualified = score >= 7
    #     except Exception:
    #         qualified = False
    #     return {"is_qualified": qualified}

    @staticmethod
    def check_if_qualified(state: GraphState):
        """
        Check if the lead is qualified based on the lead score.

        @param state: The current state of the application.
        @return: Updated state with the qualification status.
        """
        # Checking if the lead score is 6 or higher
        print(f"Score: {state['lead_score']}")
        try:
            match = re.search(r'\d+\.?\d*', str(state["lead_score"]))
            if not match:
                print(Fore.RED + "점수를 파싱할 수 없음, 불합격 처리" + Style.RESET_ALL)
                return "not qualified"
            score = float(match.group())
            is_qualified = score >= 6
        except Exception as e:
            print(Fore.RED + f"점수 변환 오류: {e}, 불합격 처리" + Style.RESET_ALL)
            return "not qualified"

        if is_qualified:
            print(Fore.GREEN + "Lead is qualified\n" + Style.RESET_ALL)
            return "qualified"
        else:
            print(Fore.RED + "Lead is not qualified\n" + Style.RESET_ALL)
            return "not qualified"
    
    @staticmethod
    def create_outreach_materials(state: GraphState):
        return {"reports": []}
    
    def generate_custom_outreach_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Crafting Custom outreach report based on gathered information -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        general_lead_search_report = get_report(reports, "General Lead Research Report")
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        
        # TODO Create better description to fetch accurate similar case study using RAG
        # get relevant case study
        case_study_report = fetch_similar_case_study(general_lead_search_report)
        
        inputs = f"""
        **Research Report:**

        {global_research_report}

        ---

        **Case Study:**

        {case_study_report}
        """
        
        # Generate report
        custom_outreach_report = invoke_llm(
            system_prompt=GENERATE_OUTREACH_REPORT_PROMPT,
            user_message=inputs,
            model="gpt-4o"
        )
        
        # TODO Find better way to include correct links into the final report
        # TODO Case study link: 실제 URL 생성 후 아래 주석 해제하여 사용
        # ** Case study link**: https://yeyak.ai/case-studies/실제URL
        # Proof read generated report
        inputs = f"""
        {custom_outreach_report}

        ---

        **Correct Links:**

        ** Our website link**: https://yeyak.ai
        """
        
        # Call our editor/proof-reader agent
        revised_outreach_report = invoke_llm(
            system_prompt=PROOF_READER_PROMPT,
            user_message=inputs,
            model="gpt-4o-mini"
        )
        
        # Store report into google docs and get shareable link
        lead = state["current_lead"]
        folder_name = f"[agent] {lead.name.strip()} ({lead.id})"
        company_name = state['company_data'].name or lead.email.split('@')[1]
        new_doc = self.docs_manager.add_document(
            content=revised_outreach_report,
            doc_title=f"Tailored Insights for {company_name}",
            folder_name=folder_name,
            make_shareable=True,
            folder_shareable=False, # Folder is private; only the document itself is shared via make_shareable
            markdown=True
        )

        if new_doc is None:
            print(Fore.RED + "Google Docs 저장 실패, 링크 없이 계속 진행" + Style.RESET_ALL)
            return {
                "custom_outreach_report_link": "",
                "reports_folder_link": ""
            }

        return {
            "custom_outreach_report_link": new_doc["shareable_url"] or "",
            "reports_folder_link": new_doc["folder_url"] or ""
        }

    def generate_personalized_email(self, state: GraphState):
        """
        Generate a personalized email for the lead.

        @param state: The current state of the application.
        @return: Updated state with the generated email.
        """
        print(Fore.YELLOW + "----- Generating personalized email -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        global_research_report = get_report(reports, "Global Lead Analysis Report")

        # Extract first name safely
        name_parts = (state["current_lead"].name or "").strip().split()
        lead_name = name_parts[0] if name_parts else "there"

        lead_data = f"""
        # **Lead First Name:** {lead_name}

        # **Lead & company Information:**

        {global_research_report}

        # Outreach report Link:

        {state["custom_outreach_report_link"]}
        """
        output = invoke_llm(
            system_prompt=PERSONALIZE_EMAIL_PROMPT,
            user_message=lead_data,
            model="gpt-4o-mini",
            response_format=EmailResponse
        )
        
        # Get relevant fields
        subject = output.subject
        personalized_email = output.email
        
        # Get lead email
        email = state["current_lead"].email
        
        # Create draft email
        gmail = GmailTools()
        try:
            gmail.create_draft_email(
                recipient=email,
                subject=subject,
                email_content=personalized_email
            )
        except Exception as e:
            print(Fore.RED + f"⚠️ Gmail draft creation failed for lead {state['current_lead'].id}: {e}" + Style.RESET_ALL)

        # Send email directly
        if SEND_EMAIL_DIRECTLY:
            try:
                gmail.send_email(
                    recipient=email,
                    subject=subject,
                    email_content=personalized_email
                )
            except Exception as e:
                print(Fore.RED + f"⚠️ Gmail send failed for lead {state['current_lead'].id}: {e}" + Style.RESET_ALL)
        
        # Save email with reports for reference
        personalized_email_doc = Report(
            title="Personalized Email",
            content=personalized_email,
            is_markdown=False
        )
        return {"reports": [personalized_email_doc]}

    def generate_interview_script(self, state: GraphState):
        print(Fore.YELLOW + "----- Generating interview script -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        
        # Generating SPIN questions
        spin_questions = invoke_llm(
            system_prompt=GENERATE_SPIN_QUESTIONS_PROMPT,
            user_message=global_research_report,
            model="gpt-4o-mini"
        )
        
        inputs = f"""
        # **Lead & company Information:**

        {global_research_report}

        # **SPIN questions:**

        {spin_questions}
        """
        
        # Generating interview script
        interview_script = invoke_llm(
            system_prompt=WRITE_INTERVIEW_SCRIPT_PROMPT,
            user_message=inputs,
            model="gpt-4o-mini"
        )
        
        interview_script_doc = Report(
            title="Interview Script",
            content=interview_script,
            is_markdown=True
        )
        
        return {"reports": [interview_script_doc]}
    
    @staticmethod
    def await_reports_creation(state: GraphState):
        return {"reports": []}
    
    def save_reports_to_google_docs(self, state: GraphState):
        print(Fore.YELLOW + "----- Save Reports to Google Docs -----\n" + Style.RESET_ALL)
        
        # Load all reports
        reports = state["reports"]
        
        # Ensure reports are saved locally (리드별 폴더에 저장)
        lead_name = state["current_lead"].name if state.get("current_lead") else ""
        save_reports_locally(reports, lead_name=lead_name)
        
        # Save all reports to Google docs
        if SAVE_TO_GOOGLE_DOCS:
            lead = state["current_lead"]
            folder_name = f"[agent] {lead.name.strip()} ({lead.id})"
            for report in reports:
                self.docs_manager.add_document(
                    content=report.content,
                    doc_title=report.title,
                    folder_name=folder_name,
                    markdown=report.is_markdown
                )

        return {}

    def update_CRM(self, state: GraphState):
        print(Fore.YELLOW + "----- Updating CRM records -----\n" + Style.RESET_ALL)
        
        # save new record data, ensure correct fields are used
        new_data = {
            "Status": "ATTEMPTED_TO_CONTACT", # Set lead to attempted contact
            "Score": state["lead_score"],
            "Analysis Reports": state.get("reports_folder_link", ""),
            "Outreach Report": state.get("custom_outreach_report_link", ""),
            "Last Contacted": get_current_date()
        }
        try:
            self.lead_loader.update_record(state["current_lead"].id, new_data)
        except Exception as e:
            print(Fore.RED + f"⚠️ CRM update failed for lead {state['current_lead'].id}: {e}" + Style.RESET_ALL)

        return {"number_leads": state["number_leads"] - 1}