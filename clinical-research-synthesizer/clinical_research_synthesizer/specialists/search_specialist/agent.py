# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines a specialist agent for performing PubMed Central searches."""

from google.adk.agents import Agent
from .tools import pmc_search

MODEL = "gemini-2.5-flash"  

# --- UPDATED INSTRUCTION ---
UPDATED_INSTRUCTION = """
Your job is to find and return the full text of a research paper from PubMed Central.

1.  Use the `search_pmc_by_title` tool with the provided paper title.
2.  Your final answer **MUST BE ONLY the full text** that is returned by the tool.
3.  If you cannot find the full text, you must respond with the text "Could not find the full text for this paper.".
"""

search_specialist = Agent(
    name="search_specialist",
    model=MODEL,
    instruction=UPDATED_INSTRUCTION, # Use the new, more specific instruction
    description="Performs a PubMed Central search and returns the full text of a paper.",
    tools=[pmc_search.search_pmc_by_title],
)