# pmc_search.py (Simplified for Debugging)
from Bio import Entrez
import xml.etree.ElementTree as ET

def extract_text_from_element(element):
    text = ""
    if element is not None:
        text = "".join(element.itertext()).strip()
    return text

def search_pmc_by_title(title_query: str, max_results: int = 1) -> str:
    """
    Simplified search for debugging. Performs only a broad topic search on PubMed Central
    and returns the full text of the first result.
    """
    Entrez.email = "ryanymt@google.com" 

    try:
        # Step 1: Broad search only
        search_handle = Entrez.esearch(db="pmc", term=title_query, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results.get("IdList", [])

        if not id_list:
            return "No results found for your query."

        # Step 2: Fetch the XML for the first ID
        fetch_handle = Entrez.efetch(db="pmc", id=id_list[0], retmode="xml")
        xml_data = fetch_handle.read()
        fetch_handle.close()

        # Step 3: Parse and extract the body text
        root = ET.fromstring(xml_data)
        article = root.find('.//article')
        if article is None:
            return "Could not find the article content in the PMC response."

        body = article.find('.//body')
        full_text = extract_text_from_element(body)
        
        if not full_text:
            return "Full text not available in this XML record."
            
        # Step 4: Return ONLY the full text
        return full_text

    except Exception as e:
        # Return a clear error message for the agent
        return f"An error occurred during the search: {e}"