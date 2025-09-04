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

search_specialist = Agent(
    name="search_specialist",
    model=MODEL,
    instruction="Your job is to find the most relevant URL for a given search query.",
    description="Performs a Google search and returns the most relevant URL.",
    tools=[google_search],
)