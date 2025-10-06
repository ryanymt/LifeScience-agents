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

"""
Tool for performing structured summarization of a research paper using a
deployed MedGemma model on Vertex AI.
"""
import os
import vertexai
from google.cloud import aiplatform
from dotenv import load_dotenv

# Load env
load_dotenv()

# Initialize Vertex AI SDK
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
)


def summarize_paper(full_text: str) -> str:
    """
    Analyzes the full text of a paper and returns a structured summary.

    This tool uses a deployed MedGemma endpoint to extract key information
    from the paper's introduction, methods, results, and conclusion.

    Args:
        full_text: The full text of the research paper.

    Returns:
        A structured summary of the paper.
    """
    endpoint_id = os.environ.get("MEDGEMMA_ENDPOINT_ID")
    if not endpoint_id:
        return "Error: MEDGEMMA_ENDPOINT_ID environment variable is not set."

    endpoint = aiplatform.Endpoint(
        endpoint_name=(
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}"
            f"/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}"
            f"/endpoints/{endpoint_id}"
        )
    )

    # A more robust prompt for structured extraction
    prompt = f"""
    You are a biomedical research assistant. Analyze the following text from a
    scientific paper and provide a detailed, structured summary. Your output
    must contain these five sections:

    1.  **Introduction**: What was the core research question or hypothesis?
    2.  **Methods**: Briefly describe the study design and methodology.
    3.  **Results**: What were the key findings and data?
    4.  **Conclusion**: What was the main takeaway or interpretation of the results?
    5.  **Key Snippets**: Include 2-3 direct quotes from the paper that highlight the most important findings or conclusions.

    ---
    PAPER TEXT:
    {full_text[:30000]}  # Truncate to fit model context window
    ---
    For every fact you extract, state the source of the information.
    """

    instances = [{"prompt": prompt}]
    try:
        response = endpoint.predict(instances=instances)
        return response.predictions[0]
    except Exception as e:
        return f"An error occurred while calling the MedGemma endpoint: {e}"