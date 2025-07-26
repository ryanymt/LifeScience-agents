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

"""Test script for the deployed Medical Research Agent."""

import os
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

FLAGS = flags.FLAGS
flags.DEFINE_string("resource_id", None, "Agent Engine resource ID.")
flags.DEFINE_string("user_id", "user", "A unique ID for the user.")
flags.mark_flag_as_required("resource_id")


def main(_):
    load_dotenv()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project_id or not location:
        raise ValueError("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set.")

    vertexai.init(project=project_id, location=location)

    agent = agent_engines.get(FLAGS.resource_id)
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"Connected to agent: {agent.display_name}")
    print("Type 'quit' to exit.")

    while True:
        user_input = input("Input: ")
        if user_input.lower() == "quit":
            break

        response = agent.query(session_id=session["id"], message=user_input)
        print(f"Response: {response.text}")


if __name__ == "__main__":
    app.run(main)