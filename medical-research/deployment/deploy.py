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

"""Deployment script for Medical Research Agent."""

import os
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from medical_research.agent import root_agent
from vertexai.preview.reasoning_engines import ReasoningEngine

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP storage bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.DEFINE_bool("list", False, "Lists all agents.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "list"])

def create_agent():
    """Creates a new Reasoning Engine for the Medical Research agent."""
    remote_agent = ReasoningEngine.create(
        root_agent,
        display_name="medical_research",
        requirements=[
            "google-adk>=1.0.0",
            "google-cloud-aiplatform>=1.93",
        ],
    )
    print(f"Created remote agent: {remote_agent.resource_name}")

def delete_agent(resource_id: str):
    """Deletes an existing Reasoning Engine."""
    remote_agent = ReasoningEngine(resource_id)
    remote_agent.delete()
    print(f"Deleted remote agent: {resource_id}")

def list_agents():
    """Lists all Reasoning Engines in the project."""
    remote_agents = ReasoningEngine.list()
    if not remote_agents:
        print("No remote agents found.")
        return

    print("All remote agents:")
    for agent in remote_agents:
        print(f"- {agent.resource_name} (Display Name: {agent.display_name})")

def main(_):
    load_dotenv()
    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    if not all([project_id, location, bucket]):
        raise ValueError(
            "Missing required config. Set GOOGLE_CLOUD_PROJECT, "
            "GOOGLE_CLOUD_LOCATION, and GOOGLE_CLOUD_STORAGE_BUCKET."
        )

    vertexai.init(project=project_id, location=location, staging_bucket=f"gs://{bucket}")

    if FLAGS.create:
        create_agent()
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