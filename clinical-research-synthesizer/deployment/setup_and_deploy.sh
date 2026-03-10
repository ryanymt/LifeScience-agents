#!/usr/bin/env bash
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

# ============================================================================
# Clinical Research Synthesizer — Full Setup & Deploy Script
#
# This script handles the complete setup and deployment:
#   1. Validates prerequisites (gcloud auth, project, APIs)
#   2. Creates a GCS staging bucket if needed
#   3. Deploys MedGemma endpoint if not already deployed
#   4. Deploys the agent to Vertex AI Agent Engine
#
# Usage:
#   ./deployment/setup_and_deploy.sh                    # Full setup + deploy
#   ./deployment/setup_and_deploy.sh --skip-medgemma    # Skip MedGemma deploy
#   ./deployment/setup_and_deploy.sh --agent-only       # Only deploy the agent
#   ./deployment/setup_and_deploy.sh --list             # List deployed agents
#   ./deployment/setup_and_deploy.sh --delete <ID>      # Delete an agent
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
fail()  { error "$*"; exit 1; }

# ── Parse flags ──────────────────────────────────────────────────────────────
SKIP_MEDGEMMA=false
AGENT_ONLY=false
LIST_AGENTS=false
DELETE_AGENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-medgemma) SKIP_MEDGEMMA=true; shift ;;
        --agent-only)    AGENT_ONLY=true; shift ;;
        --list)          LIST_AGENTS=true; shift ;;
        --delete)        DELETE_AGENT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-medgemma    Skip MedGemma endpoint deployment"
            echo "  --agent-only       Only deploy the agent (skip all setup)"
            echo "  --list             List deployed agents"
            echo "  --delete <ID>      Delete an agent by resource ID"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *) fail "Unknown option: $1" ;;
    esac
done

# ── Load .env if it exists ───────────────────────────────────────────────────
load_env() {
    if [[ -f "$ENV_FILE" ]]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi
}

# ── Save a key=value to .env ────────────────────────────────────────────────
save_env() {
    local key="$1" value="$2"
    if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
        sed -i "s|^${key}=.*|${key}=\"${value}\"|" "$ENV_FILE"
    else
        echo "${key}=\"${value}\"" >> "$ENV_FILE"
    fi
}

# ── Step 0: Prerequisites ───────────────────────────────────────────────────
check_prerequisites() {
    info "Checking prerequisites..."

    # gcloud
    command -v gcloud >/dev/null 2>&1 || fail "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
    ok "gcloud CLI found"

    # Auth
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
    [[ -n "$ACTIVE_ACCOUNT" ]] || fail "No active gcloud account. Run: gcloud auth login"
    ok "Authenticated as: $ACTIVE_ACCOUNT"

    # Python
    command -v python3 >/dev/null 2>&1 || fail "python3 not found"

    # Poetry
    if ! command -v poetry >/dev/null 2>&1; then
        warn "Poetry not found. Installing..."
        pip install poetry
    fi
    ok "Poetry available"
}

# ── Step 1: Configure project ───────────────────────────────────────────────
configure_project() {
    load_env

    # Project ID
    if [[ -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
        GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
        [[ -n "$GOOGLE_CLOUD_PROJECT" ]] || fail "No GCP project set. Run: gcloud config set project <PROJECT_ID>"
    fi
    save_env "GOOGLE_CLOUD_PROJECT" "$GOOGLE_CLOUD_PROJECT"
    ok "Project: $GOOGLE_CLOUD_PROJECT"

    # Location (global for Gemini 3.x)
    GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
    save_env "GOOGLE_CLOUD_LOCATION" "$GOOGLE_CLOUD_LOCATION"

    # Vertex AI flag
    save_env "GOOGLE_GENAI_USE_VERTEXAI" "true"

    # MedGemma location (regional)
    MEDGEMMA_LOCATION="${MEDGEMMA_LOCATION:-us-central1}"
    save_env "MEDGEMMA_LOCATION" "$MEDGEMMA_LOCATION"

    # Agent Engine deployment region
    AGENT_ENGINE_LOCATION="${AGENT_ENGINE_LOCATION:-us-central1}"
    save_env "AGENT_ENGINE_LOCATION" "$AGENT_ENGINE_LOCATION"

    load_env
}

# ── Step 2: Enable APIs ─────────────────────────────────────────────────────
enable_apis() {
    info "Enabling required GCP APIs..."
    gcloud services enable \
        aiplatform.googleapis.com \
        storage.googleapis.com \
        --project="$GOOGLE_CLOUD_PROJECT" \
        --quiet
    ok "APIs enabled"
}

# ── Step 3: Create staging bucket ────────────────────────────────────────────
setup_bucket() {
    load_env
    BUCKET="${GOOGLE_CLOUD_STORAGE_BUCKET:-}"

    if [[ -z "$BUCKET" ]]; then
        BUCKET="${GOOGLE_CLOUD_PROJECT}-agent-staging"
        info "Creating staging bucket: gs://$BUCKET"
        if ! gcloud storage buckets describe "gs://$BUCKET" --project="$GOOGLE_CLOUD_PROJECT" >/dev/null 2>&1; then
            gcloud storage buckets create "gs://$BUCKET" \
                --project="$GOOGLE_CLOUD_PROJECT" \
                --location="$MEDGEMMA_LOCATION" \
                --quiet
            ok "Bucket created: gs://$BUCKET"
        else
            ok "Bucket already exists: gs://$BUCKET"
        fi
        save_env "GOOGLE_CLOUD_STORAGE_BUCKET" "$BUCKET"
        load_env
    else
        ok "Using existing bucket: gs://$BUCKET"
    fi
}

# ── Step 4: Deploy MedGemma ─────────────────────────────────────────────────
deploy_medgemma() {
    load_env
    if [[ -n "${MEDGEMMA_ENDPOINT_ID:-}" ]]; then
        ok "MedGemma endpoint already configured: $MEDGEMMA_ENDPOINT_ID"
        return 0
    fi

    info "Deploying MedGemma 27B to Vertex AI (this takes 10-20 minutes)..."
    cd "$PROJECT_ROOT"
    poetry run python deployment/deploy_medgemma.py --nospot
    load_env

    if [[ -z "${MEDGEMMA_ENDPOINT_ID:-}" ]]; then
        fail "MedGemma deployment did not produce an endpoint ID"
    fi
    ok "MedGemma deployed: $MEDGEMMA_ENDPOINT_ID"
}

# ── Step 5: Install dependencies ────────────────────────────────────────────
install_deps() {
    info "Installing Python dependencies..."
    cd "$PROJECT_ROOT"
    poetry install --quiet 2>&1 | tail -3
    ok "Dependencies installed"
}

# ── Step 6: Deploy agent to Agent Engine ─────────────────────────────────────
deploy_agent() {
    load_env
    info "Deploying agent to Vertex AI Agent Engine..."
    cd "$PROJECT_ROOT"
    poetry run python deployment/deploy.py --create
    ok "Agent deployed to Agent Engine"
}

# ── List agents ──────────────────────────────────────────────────────────────
list_agents() {
    load_env
    cd "$PROJECT_ROOT"
    poetry run python deployment/deploy.py --list
}

# ── Delete agent ─────────────────────────────────────────────────────────────
delete_agent() {
    load_env
    cd "$PROJECT_ROOT"
    poetry run python deployment/deploy.py --delete --resource_id="$1"
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo "=============================================="
    echo "  Clinical Research Synthesizer — Deployment"
    echo "=============================================="
    echo ""

    # Handle list/delete subcommands
    if [[ "$LIST_AGENTS" == true ]]; then
        load_env
        configure_project
        list_agents
        exit 0
    fi

    if [[ -n "$DELETE_AGENT" ]]; then
        load_env
        configure_project
        delete_agent "$DELETE_AGENT"
        exit 0
    fi

    # Full deployment flow
    check_prerequisites

    if [[ "$AGENT_ONLY" == false ]]; then
        configure_project
        enable_apis
        setup_bucket
        install_deps

        if [[ "$SKIP_MEDGEMMA" == false ]]; then
            deploy_medgemma
        else
            warn "Skipping MedGemma deployment (--skip-medgemma)"
        fi
    else
        load_env
    fi

    deploy_agent

    echo ""
    echo "=============================================="
    ok "Deployment complete!"
    echo ""
    echo "  Project:           $GOOGLE_CLOUD_PROJECT"
    echo "  Agent Engine:      $AGENT_ENGINE_LOCATION"
    echo "  MedGemma Endpoint: ${MEDGEMMA_ENDPOINT_ID:-not deployed}"
    echo "  Staging Bucket:    gs://${GOOGLE_CLOUD_STORAGE_BUCKET}"
    echo ""
    echo "  To test locally:"
    echo "    poetry run adk run clinical_research_synthesizer/"
    echo ""
    echo "  To list deployed agents:"
    echo "    $0 --list"
    echo ""
    echo "=============================================="
}

main
