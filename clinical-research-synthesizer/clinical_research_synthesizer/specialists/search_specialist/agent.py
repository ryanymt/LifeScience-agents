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

"""Defines a specialist agent for performing Google searches."""

from google.adk.agents import Agent
from google.adk.tools import google_search

MODEL = "gemini-2.5-flash"  

# --- UPDATED INSTRUCTION ---
UPDATED_INSTRUCTION = """
Your job is to find the most relevant, direct, and publicly accessible PDF URL for a given search query.

1.  Analyze the search results provided by the tool.
2.  Your final answer **MUST BE ONLY a single URL** that ends with `.pdf`.
3.  **DO NOT** return any URLs that start with 'vertexaisearch.cloud.google.com'.
4.  If you cannot find a direct PDF link, you must respond with the text "Could not find a direct PDF link.".
"""

search_specialist = Agent(
    name="search_specialist",
    model=MODEL,
    instruction=UPDATED_INSTRUCTION, # Use the new, more specific instruction
    description="Performs a Google search and returns the most relevant URL.",
    tools=[google_search],
)