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

"""
Deploys MedGemma from the Vertex AI Model Garden and updates the .env file
with the resulting endpoint ID.

Uses the model_garden.OpenModel API which handles model upload, endpoint
creation, and deployment in a single call.

Usage:
    # Deploy MedGemma 1.0 27B (default) on A100 80GB spot instance:
    poetry run python deployment/deploy_medgemma.py

    # Deploy without spot instances:
    poetry run python deployment/deploy_medgemma.py --nospot

    # Deploy MedGemma 1.5 4B (multimodal, supports CT/MRI/histopathology):
    # Note: MedGemma 1.5 only comes in 4B. Use a smaller machine since 4B fits on L4.
    poetry run python deployment/deploy_medgemma.py \
        --model_id="google/medgemma@medgemma-1.5-4b-it" \
        --machine_type=g2-standard-12 \
        --accelerator_type=NVIDIA_L4

    # List available deploy options for a model:
    poetry run python deployment/deploy_medgemma.py --list_options

    # Undeploy:
    poetry run python deployment/deploy_medgemma.py --undeploy --endpoint_id=<ENDPOINT_ID>
"""

import os
import re
import sys
from pathlib import Path

from absl import app, flags
from dotenv import load_dotenv

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP region for deployment (e.g. us-central1).")
flags.DEFINE_string(
    "model_id",
    "google/medgemma@medgemma-27b-it",
    "Model Garden model ID. Format: publisher/model@version.",
)
flags.DEFINE_string(
    "machine_type",
    "a2-ultragpu-1g",
    "Machine type for the serving endpoint.",
)
flags.DEFINE_string(
    "accelerator_type",
    "NVIDIA_A100_80GB",
    "Accelerator (GPU) type.",
)
flags.DEFINE_integer("accelerator_count", 1, "Number of GPUs.")
flags.DEFINE_bool("spot", True, "Use spot/preemptible instances to reduce cost.")
flags.DEFINE_integer(
    "min_replica_count", 1, "Minimum number of serving replicas."
)
flags.DEFINE_integer(
    "max_replica_count", 1, "Maximum number of serving replicas."
)
flags.DEFINE_string(
    "display_name",
    "medgemma-clinical-research",
    "Display name for the deployed endpoint.",
)
flags.DEFINE_string("endpoint_id", None, "Endpoint ID (used with --undeploy).")
flags.DEFINE_bool("undeploy", False, "Undeploy and delete the endpoint.")
flags.DEFINE_bool("list_options", False, "List available deploy options for the model.")
flags.DEFINE_bool("accept_eula", True, "Accept the model EULA.")
flags.DEFINE_string(
    "env_file",
    None,
    "Path to .env file to update. Defaults to .env in the project root.",
)


ENV_KEY = "MEDGEMMA_ENDPOINT_ID"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_env_path() -> Path:
    if FLAGS.env_file:
        return Path(FLAGS.env_file)
    return PROJECT_ROOT / ".env"


def update_env_file(endpoint_id: str) -> None:
    """Write or update MEDGEMMA_ENDPOINT_ID in the .env file."""
    env_path = _resolve_env_path()

    if env_path.exists():
        content = env_path.read_text()
        # Replace existing key or append
        pattern = rf"^{ENV_KEY}=.*$"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(
                pattern,
                f'{ENV_KEY}="{endpoint_id}"',
                content,
                flags=re.MULTILINE,
            )
        else:
            content = content.rstrip("\n") + f'\n\n# MedGemma endpoint deployed by deploy_medgemma.py\n{ENV_KEY}="{endpoint_id}"\n'
    else:
        content = (
            "# .env - Local Environment Variables\n"
            f'GOOGLE_CLOUD_PROJECT="{os.getenv("GOOGLE_CLOUD_PROJECT", "")}"\n'
            f'GOOGLE_CLOUD_LOCATION="{os.getenv("GOOGLE_CLOUD_LOCATION", "")}"\n'
            f'GOOGLE_CLOUD_STORAGE_BUCKET="{os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "")}"\n'
            'GOOGLE_GENAI_USE_VERTEXAI="true"\n'
            f'\n# MedGemma endpoint deployed by deploy_medgemma.py\n'
            f'{ENV_KEY}="{endpoint_id}"\n'
        )

    env_path.write_text(content)
    print(f"\n.env updated: {ENV_KEY}=\"{endpoint_id}\" in {env_path}")


def deploy_medgemma(open_model) -> str:
    """Deploy MedGemma from Model Garden and return the endpoint ID."""
    spot_label = " (spot)" if FLAGS.spot else ""
    print(
        f"Deploying {FLAGS.model_id}\n"
        f"  machine={FLAGS.machine_type}, "
        f"gpu={FLAGS.accelerator_type} x{FLAGS.accelerator_count}{spot_label}\n"
        f"This may take 10-20 minutes..."
    )

    endpoint = open_model.deploy(
        accept_eula=FLAGS.accept_eula,
        machine_type=FLAGS.machine_type,
        accelerator_type=FLAGS.accelerator_type,
        accelerator_count=FLAGS.accelerator_count,
        min_replica_count=FLAGS.min_replica_count,
        max_replica_count=FLAGS.max_replica_count,
        spot=FLAGS.spot,
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20250430_0916_RC00_maas",
        endpoint_display_name=FLAGS.display_name,
        model_display_name=FLAGS.display_name,
        use_dedicated_endpoint=True,
        reservation_affinity_type="NO_RESERVATION",
        deploy_request_timeout=1800,
    )

    endpoint_id = endpoint.name
    print(f"\nDeployment complete! Endpoint ID: {endpoint_id}")
    return endpoint_id


def undeploy_medgemma(endpoint_id: str) -> None:
    """Undeploy all models from the endpoint and delete it."""
    from google.cloud import aiplatform

    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("MEDGEMMA_LOCATION", "us-central1")
    endpoint = aiplatform.Endpoint(
        endpoint_name=(
            f"projects/{project_id}"
            f"/locations/{location}"
            f"/endpoints/{endpoint_id}"
        )
    )
    print(f"Undeploying all models from endpoint {endpoint_id}...")
    endpoint.undeploy_all()
    print("Deleting endpoint...")
    endpoint.delete()
    print(f"Endpoint {endpoint_id} deleted.")

    # Clear from .env
    env_path = _resolve_env_path()
    if env_path.exists():
        content = env_path.read_text()
        pattern = rf'^{ENV_KEY}=.*$'
        content = re.sub(pattern, f'{ENV_KEY}=""', content, flags=re.MULTILINE)
        env_path.write_text(content)
        print(f".env updated: {ENV_KEY} cleared.")


def main(_):
    load_dotenv()

    import vertexai
    from vertexai.preview import model_garden

    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    # MedGemma deployment is regional — use MEDGEMMA_LOCATION (not GOOGLE_CLOUD_LOCATION
    # which may be "global" for Gemini 3.x inference).
    location = FLAGS.location or os.getenv("MEDGEMMA_LOCATION", "us-central1")

    if not project_id:
        print("Error: --project_id flag or GOOGLE_CLOUD_PROJECT env var required.")
        sys.exit(1)

    vertexai.init(project=project_id, location=location)

    if FLAGS.list_options:
        open_model = model_garden.OpenModel(FLAGS.model_id)
        options = open_model.list_deploy_options()
        for i, opt in enumerate(options):
            ms = opt.dedicated_resources.machine_spec
            print(
                f"[{i}] {opt.deploy_task_name}: "
                f"machine={ms.machine_type}, "
                f"gpu={ms.accelerator_type} x{ms.accelerator_count}"
            )
    elif FLAGS.undeploy:
        endpoint_id = FLAGS.endpoint_id or os.getenv(ENV_KEY)
        if not endpoint_id:
            print("Error: --endpoint_id flag or MEDGEMMA_ENDPOINT_ID env var required for undeploy.")
            sys.exit(1)
        undeploy_medgemma(endpoint_id)
    else:
        open_model = model_garden.OpenModel(FLAGS.model_id)
        endpoint_id = deploy_medgemma(open_model)
        update_env_file(endpoint_id)
        print("\nDone! You can now run the agent with:")
        print("  poetry run adk run clinical_research_synthesizer/")


if __name__ == "__main__":
    app.run(main)
