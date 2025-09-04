"""
Tool for scraping the eligibility criteria directly from a ClinicalTrials.gov webpage.
"""
import requests
from bs4 import BeautifulSoup

def scrape_criteria_from_url(trial_id: str) -> str:
    """
    Given a clinical trial ID, scrapes the webpage and extracts the full text
    of the "Participation Criteria" section, which includes both inclusion and
    exclusion criteria.

    Args:
        trial_id: The NCT ID for the clinical trial (e.g., "NCT04468659").

    Returns:
        The raw text of the eligibility criteria, or an error message.
    """
    try:
        url = f"https://clinicaltrials.gov/study/{trial_id}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the H2 heading with the text "Participation Criteria"
        heading = soup.find('h2', string="Participation Criteria")

        if not heading:
            return f"Could not find the 'Participation Criteria' heading for trial ID: {trial_id}."

        # The full criteria is contained within the div that immediately follows the heading
        criteria_section = heading.find_next_sibling("div")

        if not criteria_section:
            return f"Could not find the criteria section for trial ID: {trial_id}."

        # Use .get_text() with a separator to maintain line breaks for readability
        full_text = criteria_section.get_text(separator='\\n', strip=True)

        if not full_text.strip():
            return f"Found the participation criteria section for {trial_id}, but it contained no text."

        return f"Successfully scraped participation criteria for {trial_id}:\\n\\n{full_text}"

    except requests.exceptions.RequestException as e:
        return f"Failed to download webpage for trial ID {trial_id}. Error: {e}"
    except Exception as e:
        return f"An error occurred while scraping the page for {trial_id}. Error: {e}"

# To test this script as a regular Python file, you can add the following:
if __name__ == '__main__':
    test_trial_id = "NCT04468659"
    print(scrape_criteria_from_url(test_trial_id))