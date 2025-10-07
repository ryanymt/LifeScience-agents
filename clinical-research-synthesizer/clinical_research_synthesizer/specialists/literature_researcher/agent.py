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

"""Defines the specialist 'literature_researcher' agent."""

from google.adk.agents import Agent
from . import prompt

# tools import
from .tools import (
    fetch_articles,
    extract_text_from_pdf,
    summarize_paper_with_medgemma,
)

MODEL = "gemini-2.5-pro"

literature_researcher = Agent(
    name="literature_researcher",
    model=MODEL,
    instruction=prompt.LITERATURE_RESEARCHER_PROMPT,
    description=(
        "Finds, retrieves the full text of, and performs structured analysis on "
        "scientific papers from PubMed and the web."
    ),
    tools=[
        #fetch_articles.fetch_pubmed_articles,
        extract_text_from_pdf.extract_pdf_text_from_url, 
        summarize_paper_with_medgemma.summarize_paper,
    ],
)