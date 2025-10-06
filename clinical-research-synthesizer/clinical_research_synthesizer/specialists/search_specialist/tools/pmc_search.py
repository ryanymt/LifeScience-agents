# pmc_search.py
# A Python script to search for research literature in PubMed Central (PMC).
# This script uses the Biopython library to query the NCBI Entrez API.

from Bio import Entrez
import xml.etree.ElementTree as ET

def extract_text_from_element(element):
    """
    Recursively extracts and joins text from an XML element and its children,
    ensuring a readable format.
    """
    text = ""
    if element is not None:
        # Join text content of the element and all its children
        text = "".join(element.itertext()).strip()
    return text

def search_pmc_by_title(title_query: str, max_results: int = 1) -> str:
    """
    Searches PubMed Central for a given exact title. If no results are found,
    it automatically retries with a broader topic search.

    Args:
        title_query (str): The exact title of the article to search for.
        max_results (int): The maximum number of results to retrieve.
        
    Returns:
        A formatted string containing the full text of the article, or an
        error message if the article is not found.
    """
    Entrez.email = "ryanymt@google.com" 

    exact_title_query = f'"{title_query}"[Title]'
    
    try:
        search_handle = Entrez.esearch(db="pmc", term=exact_title_query, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results["IdList"]

        if not id_list:
            search_handle = Entrez.esearch(db="pmc", term=title_query, retmax=max_results)
            search_results = Entrez.read(search_handle)
            search_handle.close()
            id_list = search_results["IdList"]

        if not id_list:
            return "No results found for your query."

        fetch_handle = Entrez.efetch(db="pmc", id=id_list, retmode="xml")
        xml_data = fetch_handle.read()
        fetch_handle.close()

        root = ET.fromstring(xml_data)

        article = root.find('.//article')
        if article is None:
            return "Could not find the article in the PMC response."

        full_text = extract_text_from_element(article.find('.//body'))
        
        if not full_text:
            return "Full text not available in this XML record."
            
        return full_text

    except ET.ParseError as e:
        return f"An error occurred while parsing the XML response from PubMed: {e}"
    except Exception as e:
        return f"An error occurred: {e}"