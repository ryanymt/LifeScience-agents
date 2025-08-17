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

"""Defines the specialist 'compound_analyzer' agent."""

from google.adk.agents import Agent
from . import prompt
from .tools import predict_toxicity

# A standard, fast model is sufficient for this agent's reasoning.
MODEL = "gemini-2.5-flash"

compound_analyzer = Agent(
    name="compound_analyzer",
    model=MODEL,
    instruction=prompt.COMPOUND_ANALYZER_PROMPT,
    description="Analyzes chemical compounds to predict properties like toxicity.",
    tools=[predict_toxicity.predict_clinical_toxicity],
)
