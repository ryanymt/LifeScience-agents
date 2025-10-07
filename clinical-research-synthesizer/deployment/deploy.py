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

"""Deployment script for the Clinical Research Synthesizer Agent."""

import os
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from clinical_research_synthesizer.agent import root_agent
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP storage bucket for staging.")
flags.DEFINE_string("resource_id", None, "Agent Engine resource ID for deletion.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.DEFINE_bool("list", False, "Lists all agents.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "list"])


def create_agent(env_vars):
    """Creates a new Agent Engine for the Clinical Research Synthesizer."""
    adk_app = AdkApp(agent=root_agent)
    remote_agent = agent_engines.create(
        adk_app,
        display_name="clinical-research-synthesizer", # New agent name
        requirements=[
            "google-adk>=0.2.1",
            "google-cloud-aiplatform>=1.55.0",
            "python-dotenv>=1.0.1",
            "biopython>=1.83",
            "pubchempy>=1.0.4",
            "requests>=2.32.0",
            "PyPDF2>=3.0.0",
            "beautifulsoup4>=4.12.0",
        ],
        extra_packages=["./clinical_research_synthesizer"],
        env_vars=env_vars,
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete_agent(resource_id: str):
    """Deletes an existing Agent Engine."""
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f" Deleted remote agent: {resource_id}")


def list_agents():
    """Lists all Agent Engines in the project."""
    remote_agents = agent_engines.list()
    if not remote_agents:
        print("No remote agents found.")
        return

    print("All remote agents:")
    for agent in remote_agents:
        print(f"- {agent.name} (Display Name: {agent.display_name})")


def main(_):
    load_dotenv()
    env_vars = {}

    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    # Load secrets from the .env file for the agent engine.
    # need IDs for MedGemma and TxGemma Chat.
    env_vars["MEDGEMMA_ENDPOINT_ID"] = os.getenv("MEDGEMMA_ENDPOINT_ID")
    #env_vars["TXGEMMA_CHAT_ENDPOINT_ID"] = os.getenv("TXGEMMA_CHAT_ENDPOINT_ID")

    if not all(
        [
            project_id,
            location,
            bucket,
            env_vars["MEDGEMMA_ENDPOINT_ID"],
        #    env_vars["TXGEMMA_CHAT_ENDPOINT_ID"],
        ]
    ):
        raise ValueError(
            "Missing required config. Set all required variables in your "
            ".env file or as flags."
        )

    vertexai.init(
        project=project_id, location=location, staging_bucket=f"gs://{bucket}"
    )

    if FLAGS.create:
        create_agent(env_vars)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            raise ValueError("The --resource_id flag is required to delete an agent.")
        delete_agent(FLAGS.resource_id)
    elif FLAGS.list:
        list_agents()
    else:
        print("No action specified. Use --create, --delete, or --list.")


if __name__ == "__main__":
    app.run(main)