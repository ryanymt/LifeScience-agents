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

"""Custom tool for interacting with the MedGemma endpoint."""

import os
from google.cloud.aiplatform import Endpoint

import vertexai

# Initialize the Vertex AI SDK
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
)

def query_medical_knowledge(question: str) -> str:
    """
    Answers a general medical question using the MedGemma model.

    Args:
        question: The user's question about a medical topic.

    Returns:
        A string containing the answer from the MedGemma model.
    """
    endpoint = Endpoint(
        endpoint_name=(
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}"
            f"/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}"
            f"/endpoints/{os.environ['MEDGEMMA_ENDPOINT_ID']}"
        )
    )

    # Send the user's question directly to the MedGemma endpoint
    response = endpoint.predict(instances=[{"prompt": question}])

    # Extract the prediction string from the response
    prediction = response.predictions[0]

    # Append the required disclaimer
    disclaimer = (
        "\n\nThis information is for educational purposes only. Please consult "
        "a qualified healthcare professional for any medical concerns."
    )
    return prediction + disclaimer