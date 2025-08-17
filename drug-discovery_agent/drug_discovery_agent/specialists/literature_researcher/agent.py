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
from .tools import fetch_articles, therapeutics_chat

MODEL = "gemini-2.5-flash"

literature_researcher = Agent(
    name="literature_researcher",
    model=MODEL,
    instruction=prompt.LITERATURE_RESEARCHER_PROMPT,
    description="Searches scientific articles on PubMed or answers general therapeutic questions.",
    tools=[
        fetch_articles.fetch_pubmed_articles,
        therapeutics_chat.ask_therapeutics_expert
    ],
)
