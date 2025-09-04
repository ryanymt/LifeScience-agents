# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for searching for clinical trials on ClinicalTrials.gov."""

import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def search_trials(search_query: str) -> str:
    """
    Searches ClinicalTrials.gov for a query and returns top 3 results.

    Args:
        search_query: The drug, condition, or keywords to search for.

    Returns:
        A formatted string with the titles and NCT IDs of the top 3 results,
        or an error message.
    """
    params = {
        "query.term": search_query,
        "pageSize": 3,
        "format": "json",
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("studies"):
            return f"No clinical trials found for the query: '{search_query}'."

        results = []
        for study in data["studies"]:
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            title = id_module.get("officialTitle", "No title available")
            nct_id = id_module.get("nctId", "No ID available")
            results.append(f"- Title: {title}\n  ID: {nct_id}")

        return (
            "Found the following clinical trials:\n"
            + "\n".join(results)
            + "\n\nPlease use the `extract_criteria` tool for each ID to get "
            "the pre-conditions."
        )

    except requests.exceptions.RequestException as e:
        return f"An error occurred while searching for clinical trials: {e}"