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

"""Tool for predicting clinical toxicity using a TxGemma Vertex AI endpoint."""

import os
import vertexai
from google.cloud import aiplatform

# Initialize Vertex AI SDK
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
)

def predict_clinical_toxicity(smiles_string: str) -> str:
    """
    Predicts if a drug is toxic in human clinical trials via a Vertex AI endpoint.

    Args:
        smiles_string: The SMILES string representation of the drug.

    Returns:
        A string containing the toxicity prediction.
    """
    # This environment variable must be set to your deployed TxGemma endpoint ID.
    endpoint_id = os.environ.get("TXGEMMA_PREDICT_ENDPOINT_ID")
    if not endpoint_id:
        return "Error: TXGEMMA_PREDICT_ENDPOINT_ID environment variable is not set."

    endpoint = aiplatform.Endpoint(
        endpoint_name=(
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}"
            f"/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}"
            f"/endpoints/{endpoint_id}"
        )
    )

    # This prompt format is specific to the ClinTox task for TxGemma.
    prompt = (
        "Instructions: Answer the following question about drug properties.\n"
        "Context: The assessment of clinical toxicity is a critical component of drug development. "
        "A compound's potential to cause adverse effects in humans can determine its viability as a therapeutic agent.\n"
        "Question: Given a drug SMILES string, predict whether it has a toxicity risk in human clinical trials.\n"
        "(A) No toxicity risk\n(B) Has a toxicity risk\n"
        f"Drug SMILES: {smiles_string}"
    )

    # The instance format for Vertex AI predictions is a list of dictionaries.
    instances = [{"prompt": prompt}]
    response = endpoint.predict(instances=instances)
    
    prediction = response.predictions[0]

    # Process the raw prediction into a more descriptive result.
    if "A" in prediction:
        return f"The compound '{smiles_string}' is predicted to NOT be toxic."
    elif "B" in prediction:
        return f"The compound '{smiles_string}' is predicted to BE toxic."
    else:
        return f"Could not determine toxicity. Raw model output: {prediction}"
