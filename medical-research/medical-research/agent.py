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

"""Medical_Research: Medical advice, chemical compound and protein analysis."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
# The imports are now simpler, coming from the sub_agents package.
from .sub_agents import medical_analyst_agent, medical_search_agent

#from .sub_agents.academic_newresearch import academic_newresearch_agent
#from .sub_agents.academic_websearch import academic_websearch_agent


MODEL = "gemini-2.5-pro"


medical_coordinator = LlmAgent(
    name="medical_coordinator",
    model=MODEL,
    description=(
        "Responds to general medical questions and analyzes chemical"
        " compounds and proteins."
    ),
    instruction=prompt.MEDICAL_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=medical_search_agent),
        AgentTool(agent=medical_analyst_agent),
    ],
)

root_agent = medical_coordinator