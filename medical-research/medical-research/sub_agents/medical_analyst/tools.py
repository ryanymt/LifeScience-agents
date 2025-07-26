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

"""Custom tool for interacting with the TxGemma endpoint."""

import os
import vertexai
from google.cloud.aiplatform import Endpoint

# Initialize the Vertex AI SDK
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
)

def predict_bbb_crossing(smiles_string: str) -> str:
    """
    Predicts whether a drug crosses the blood-brain barrier (BBB).

    Args:
        smiles_string: The SMILES string representation of the drug.

    Returns:
        A string containing the prediction.
    """
    endpoint = Endpoint(
        endpoint_name=(
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}"
            f"/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}"
            f"/endpoints/{os.environ['TXGEMMA_ENDPOINT_ID']}"
        )
    )

    prompt = (
        "Instructions: Answer the following question about drug properties.\n"
        "Context: As a membrane separating circulating blood and brain "
        "extracellular fluid, the blood-brain barrier (BBB) is the "
        "protection layer that blocks most foreign drugs. Thus the ability "
        "of a drug to penetrate the barrier to deliver to the site of "
        "action forms a crucial challenge in development of drugs for "
        "central nervous system.\n"
        "Question: Given a drug SMILES string, predict whether it\n"
        "(A) does not cross the BBB (B) crosses the BBB\n"
        f"Drug SMILES: {smiles_string}"
    )

    response = endpoint.predict(instances=[{"prompt": prompt}])
    
    # Corrected line: Access the prediction as a direct string element.
    prediction = response.predictions[0]

    return prediction