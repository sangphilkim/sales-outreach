import os
import warnings
from colorama import Fore, Style
warnings.filterwarnings("ignore", message="Pydantic serializer warnings.*", category=UserWarning)
from dotenv import load_dotenv
from src.graph import OutReachAutomation
from src.state import *
# from src.tools.leads_loader.airtable import AirtableLeadLoader
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader
# from src.tools.leads_loader.hubspot import HubSpotLeadLoader

# Load environment variables from a .env file
load_dotenv()

if __name__ == "__main__":
    # Use Airtable for accessing your leads list
    # lead_loader = AirtableLeadLoader(
    #     access_token=os.getenv("AIRTABLE_ACCESS_TOKEN"),
    #     base_id=os.getenv("AIRTABLE_BASE_ID"),
    #     table_name=os.getenv("AIRTABLE_TABLE_NAME"),
    # )

    # Use Sheet for accessing your leads list
    lead_loader = GoogleSheetLeadLoader(
        spreadsheet_id=os.getenv("SHEET_ID"),
    )

    # Use HubSpot for accessing your leads list
    # lead_loader = HubSpotLeadLoader(
    #     access_token=os.getenv("HUBSPOT_API_KEY"),
    # )

    # Instantiate the OutReachAutomation class
    automation = OutReachAutomation(lead_loader)
    app = automation.app
    
    # initial graph inputs:
    # Lead ids to be processed, leave empty to fetch all news leads
    inputs = {"leads_ids": []}


    # Run the outreach automation with the provided lead name and email
    lead_ids = inputs.get('leads_ids', [])
    run_label = lead_ids[0] if lead_ids else "all-new-leads"
    config = {
        'recursion_limit': 10000,
        'run_name': f"riad-{run_label}",
        'metadata': {'project': 'riad-agent', 'leads_ids': lead_ids}
    }
    app.invoke(inputs, config)
    print(Fore.GREEN + "✅ Outreach automation completed." + Style.RESET_ALL)