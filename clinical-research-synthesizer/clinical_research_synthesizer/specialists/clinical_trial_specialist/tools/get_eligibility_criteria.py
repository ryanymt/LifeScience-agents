import json
import requests

def get_eligibility_criteria_from_api(trial_id: str) -> str:
    """
    Fetches clinical trial data from the ClinicalTrials.gov API and extracts
    the full text of the eligibility criteria.

    Args:
        trial_id: The NCT ID of the clinical trial (e.g., "NCT04468659").

    Returns:
        The raw text of the eligibility criteria, or an error message.
    """
    # API endpoint for a specific study.
    # We can specify the exact field we want: protocolSection.eligibilityModule.eligibilityCriteria
    url = f"https://clinicaltrials.gov/api/v2/studies/{trial_id}?fields=protocolSection.eligibilityModule.eligibilityCriteria"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        
        # Navigate the JSON structure to get the criteria text
        eligibility_criteria = (
            data.get("protocolSection", {})
            .get("eligibilityModule", {})
            .get("eligibilityCriteria", "")
        )

        if not eligibility_criteria:
            return f"No eligibility criteria text found for trial ID: {trial_id}."
            
        return f"Successfully retrieved eligibility criteria for {trial_id}:\\n\\n{eligibility_criteria}"

    except requests.exceptions.HTTPError as errh:
        if response.status_code == 404:
            return f"Error: Trial ID '{trial_id}' not found."
        return f"Http Error: {errh}"
    except requests.exceptions.RequestException as err:
        return f"An unexpected error occurred while fetchiqng API data: {err}"

# test this script as a regular Python file
#if __name__ == '__main__':
#    test_trial_id = "NCT04468659"
#    print(get_eligibility_criteria_from_api(test_trial_id))