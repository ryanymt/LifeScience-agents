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

# Maintainer : ryanymt@google.com

"""Defines the main 'research_coordinator' agent for the Clinical Research Synthesizer."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool


from . import prompt
# Import all three specialist agents
from .specialists.literature_researcher import (
    agent as literature_researcher_agent,
)
from .specialists.clinical_trial_specialist import (
    agent as clinical_trial_specialist_agent,
)
from .specialists.search_specialist import (
    agent as search_specialist_agent,
)

# Use a powerful model for the coordinator's reasoning and planning.
MODEL = "gemini-2.5-pro"

research_coordinator = LlmAgent(
    name="research_coordinator",
    model=MODEL,
    description="The main agent that synthesizes clinical research.",
    instruction=prompt.RESEARCH_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=literature_researcher_agent.literature_researcher),
        AgentTool(agent=clinical_trial_specialist_agent.clinical_trial_specialist),
        AgentTool(agent=search_specialist_agent.search_specialist),
    ],
)

# The root_agent is the entry point for the ADK.
root_agent = research_coordinator