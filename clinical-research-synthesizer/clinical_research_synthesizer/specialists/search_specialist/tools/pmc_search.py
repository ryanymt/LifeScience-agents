# pmc_search.py
from Bio import Entrez
import xml.etree.ElementTree as ET


def extract_text_from_element(element):
    text = ""
    if element is not None:
        text = "".join(element.itertext()).strip()
    return text


def search_pmc_by_title(title_query: str, max_results: int = 1) -> str:
    """
    Searches PubMed Central for a topic and returns the full text of the first result.

    Args:
        title_query: The topic, title, or keywords to search for.
        max_results: Maximum number of results to fetch (default 1).

    Returns:
        The article title, PMC ID, and full body text, or an error message.
    """
    Entrez.email = "ryanymt@google.com"

    try:
        # Step 1: Search PMC
        search_handle = Entrez.esearch(db="pmc", term=title_query, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results.get("IdList", [])

        if not id_list:
            return f"No results found on PubMed Central for: '{title_query}'."

        pmc_id = id_list[0]

        # Step 2: Fetch the XML for the first ID
        fetch_handle = Entrez.efetch(db="pmc", id=pmc_id, retmode="xml")
        xml_data = fetch_handle.read()
        fetch_handle.close()

        # Step 3: Parse and extract article metadata + body text
        root = ET.fromstring(xml_data)
        article = root.find('.//article')
        if article is None:
            return "Could not find the article content in the PMC response."

        # Extract title
        title_el = article.find('.//article-title')
        title = extract_text_from_element(title_el) if title_el is not None else "Unknown title"

        # Extract body text
        body = article.find('.//body')
        full_text = extract_text_from_element(body)

        if not full_text:
            return f"Full text not available for PMC{pmc_id}: '{title}'."

        # Step 4: Return title, PMC ID, and full text
        return f"Title: {title}\nPMC ID: PMC{pmc_id}\n\n{full_text}"

    except Exception as e:
        return f"An error occurred during the PMC search: {e}"