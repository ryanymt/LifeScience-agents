"""
Tool for scraping the eligibility criteria directly from a ClinicalTrials.gov webpage.
"""
import requests
from bs4 import BeautifulSoup, NavigableString

def scrape_criteria_from_url(trial_id: str) -> str:
    """
    Given a clinical trial ID, scrapes the webpage and extracts the full text
    of the eligibility criteria section. This version is more robust to HTML changes.

    Args:
        trial_id: The NCT ID for the clinical trial (e.g., "NCT04468659").

    Returns:
        The raw text of the eligibility criteria, or an error message.
    """
    try:
        # The study URL is now at /study/ not /ct2/show/
        url = f"https://clinicaltrials.gov/study/{trial_id}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the H2 heading with the text "Eligibility Criteria"
        heading = soup.find('h2', string="Eligibility Criteria")

        if not heading:
            return f"Could not find the 'Eligibility Criteria' heading for trial ID: {trial_id}."

        # Collect all text in the siblings following the heading until the next H2
        content = []
        for sibling in heading.find_next_siblings():
            if sibling.name == 'h2':
                break  # Stop when we hit the next major section
            if isinstance(sibling, NavigableString):
                continue # Ignore stray strings
            content.append(sibling.get_text(separator='\\n', strip=True))

        full_text = "\\n".join(content)

        if not full_text.strip():
            return f"Found the eligibility section for {trial_id}, but it contained no text."

        return f"Successfully scraped eligibility criteria for {trial_id}:\\n\\n{full_text}"

    except requests.exceptions.RequestException as e:
        return f"Failed to download webpage for trial ID {trial_id}. Error: {e}"
    except Exception as e:
        return f"An error occurred while scraping the page for {trial_id}. Error: {e}"