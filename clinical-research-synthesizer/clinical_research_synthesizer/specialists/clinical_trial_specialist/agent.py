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

"""Defines the specialist 'clinical_trial_specialist' agent."""

from google.adk.agents import Agent
from . import prompt
from .tools import search_clinical_trials, get_eligibility_criteria
#from .tools import search_clinical_trials, scrape_trial_criteria 
#from .tools import search_clinical_trials, extract_preconditions


# Use a powerful model for analysis and extraction.
MODEL = "gemini-2.5-pro"

clinical_trial_specialist = Agent(
    name="clinical_trial_specialist",
    model=MODEL,
    instruction=prompt.CLINICAL_TRIAL_PROMPT,
    description=(
        "Searches for clinical trials and extracts pre-condition information "
        "(inclusion and exclusion criteria) from them."
    ),
    tools=[
        search_clinical_trials.search_trials,
        get_eligibility_criteria.get_eligibility_criteria_from_api,
        # scrape_trial_criteria.scrape_criteria_from_url,
       # extract_preconditions.extract_criteria,
    ],
)