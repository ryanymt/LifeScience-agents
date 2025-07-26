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

"""Test cases for the Medical Research agent."""

import dotenv
import pytest
from medical_research.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Loads environment variables from a .env file."""
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_routes_to_medical_search():
    """
    Tests if a general medical question routes to the Medical Search Agent.
    We expect a disclaimer in the response.
    """
    # Use the correct package name (with an underscore).
    app_name = "medical_research"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user_search"
    )

    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=types.Content(parts=[types.Part(text="What are the common symptoms of diabetes?")]),
    ):
        if event.content.parts and event.content.parts[0].text:
            response += event.content.parts[0].text

    # Check for the disclaimer from the Medical Search Agent's prompt.
    assert "consult a qualified healthcare professional" in response.lower()


@pytest.mark.asyncio
async def test_routes_to_medical_analyst():
    """
    Tests if a technical SMILES question routes to the Medical Analyst Agent.
    We expect a prediction about the BBB.
    """
    # Use the correct package name (with an underscore).
    app_name = "medical_research"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user_analyst"
    )

    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=types.Content(parts=[types.Part(text="For SMILES CN1C(=O)CN=C(C2=CCCCC2)c2cc(Cl)ccc21, does it cross the BBB?")]),
    ):
        if event.content.parts and event.content.parts[0].text:
            response += event.content.parts[0].text

    # Check for keywords from the Medical Analyst Agent's task.
    assert "bbb" in response.lower() and (
        "crosses" in response.lower() or "does not cross" in response.lower()
    )