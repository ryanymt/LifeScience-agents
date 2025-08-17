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

"""Tool for general therapeutic questions using a TxGemma Chat Vertex AI endpoint."""

import os
import vertexai
from google.cloud import aiplatform

# Initialize Vertex AI SDK
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
)

def ask_therapeutics_expert(query: str) -> str:
    """
    Answers general therapeutics questions using a TxGemma chat model.

    Args:
        query: The user's question about a therapeutic topic.

    Returns:
        A string containing the answer from the chat model.
    """
    # This environment variable must be set to your deployed TxGemma chat endpoint ID.
    endpoint_id = os.environ.get("TXGEMMA_CHAT_ENDPOINT_ID")
    if not endpoint_id:
        return "Error: TXGEMMA_CHAT_ENDPOINT_ID environment variable is not set."

    endpoint = aiplatform.Endpoint(
        endpoint_name=(
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}"
            f"/locations/{os.environ['GOOGLE_CLOUD_LOCATION']}"
            f"/endpoints/{endpoint_id}"
        )
    )

    # The chat model uses a simpler prompt format.
    instances = [{"prompt": query}]
    response = endpoint.predict(instances=instances)
    
    return response.predictions[0]
