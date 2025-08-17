# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for searching for articles on PubMed."""

from Bio import Medline, Entrez

def fetch_pubmed_articles(search_query: str) -> str:
    """
    Searches PubMed for a query and returns abstracts of the top 3 articles.

    Args:
        search_query: The topic or keywords to search for.

    Returns:
        A formatted string with the titles and abstracts of the search results.
    """
    # NCBI requires you to identify yourself with an email address.
    Entrez.email = "your.email@example.com"  # Please replace with your email

    try:
        handle = Entrez.esearch(db="pubmed", sort="relevance", term=search_query, retmax=3)
        record = Entrez.read(handle)
        pmids = record.get("IdList", [])
        handle.close()

        if not pmids:
            return f"No PubMed articles were found for the query: '{search_query}'."

        fetch_handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="medline", retmode="text")
        records = list(Medline.parse(fetch_handle))
        fetch_handle.close()

        result_str = f"Top 3 PubMed results for '{search_query}':\n"
        for i, record in enumerate(records, start=1):
            title = record.get("TI", "No title available")
            abstract = record.get("AB", "No abstract available")
            result_str += f"\n--- Article #{i} ---\nTitle: {title}\nAbstract: {abstract}\n"
        
        return result_str

    except Exception as e:
        return f"An error occurred while searching PubMed: {e}"
