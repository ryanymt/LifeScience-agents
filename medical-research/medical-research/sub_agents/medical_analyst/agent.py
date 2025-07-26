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

"""Medical_analyst_agent for analyzing chemical compounds and proteins."""

from google.adk.agents import Agent
from . import prompt
# Import our new custom tool
from . import tools

# The agent will use a standard model to decide when to call the tool.
MODEL = "gemini-2.5-pro"

medical_analyst_agent = Agent(
    model=MODEL,
    name="medical_analyst_agent",
    instruction=prompt.MEDICAL_ANALYST_PROMPT,
    # Give the agent its new tool
    tools=[tools.predict_bbb_crossing],
)