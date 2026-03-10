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
# Deploy Agent Engine Agent to Gemini Enterprise (formerly AgentSpace)
#
# Registers a Vertex AI Agent Engine agent with Gemini Enterprise so it
# appears in the Gemini Enterprise web app for end users.
#
# ============================================================================
# PREREQUISITES
# ============================================================================
#
# 1. Deploy the agent to Vertex AI Agent Engine first:
#      ./deployment/setup_and_deploy.sh
#    Or directly:
#      poetry run python deployment/deploy.py --create
#    Note the reasoning engine resource ID from the output (e.g. "1234567890").
#
# 2. Create a Gemini Enterprise app in the Google Cloud console:
#      https://console.cloud.google.com/gen-app-builder/engines
#    Note the app ID from the URL or app settings.
#
# 3. Ensure you have the required IAM role:
#      gcloud projects add-iam-policy-binding PROJECT_ID \
#        --member="user:YOUR_EMAIL" \
#        --role="roles/discoveryengine.admin"
#
# 4. The Discovery Engine API will be auto-enabled by this script, or manually:
#      gcloud services enable discoveryengine.googleapis.com --project=PROJECT_ID
#
# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================
#
# Set these in your .env file (or pass as CLI flags). The script loads .env
# automatically from the project root.
#
# Required:
#   GOOGLE_CLOUD_PROJECT          GCP project ID (e.g. "my-project-123")
#   GOOGLE_CLOUD_PROJECT_NUMBER   GCP numeric project number (e.g. "123456789012")
#                                 If not set, the script auto-resolves it via gcloud.
#   AGENT_ENGINE_RESOURCE_ID      Reasoning engine ID from deploy.py output
#                                 (e.g. "1234567890")
#   GEMINI_ENTERPRISE_APP_ID      Gemini Enterprise app ID from the console
#                                 (e.g. "my-research-app_1234567890")
#
# Optional:
#   AGENT_ENGINE_LOCATION          Region where Agent Engine is deployed
#                                  (default: us-central1)
#   GEMINI_ENTERPRISE_LOCATION     Discovery Engine multi-region: global | us | eu
#                                  (default: global)
#   AGENT_DISPLAY_NAME             Name shown to users in Gemini Enterprise
#                                  (default: "Clinical Research Synthesizer")
#   AGENT_DESCRIPTION              Description shown to users
#                                  (default: auto-generated)
#   AGENT_ICON_URI                 Public URL for the agent icon
#                                  (default: Google Science icon)
#
# Example .env entries:
#   GOOGLE_CLOUD_PROJECT="my-project-123"
#   GOOGLE_CLOUD_PROJECT_NUMBER="123456789012"
#   AGENT_ENGINE_RESOURCE_ID="9876543210"
#   AGENT_ENGINE_LOCATION="us-central1"
#   GEMINI_ENTERPRISE_APP_ID="my-research-app_1234567890"
#   GEMINI_ENTERPRISE_LOCATION="global"
#   AGENT_DISPLAY_NAME="Clinical Research Synthesizer"
#
# ============================================================================
# USAGE
# ============================================================================
#
# Register (connect) the agent to Gemini Enterprise:
#   ./deployment/deploy_to_gemini_enterprise.sh --register
#
# Register with all parameters as flags (no .env needed):
#   ./deployment/deploy_to_gemini_enterprise.sh --register \
#     --project my-project-123 \
#     --project-number 123456789012 \
#     --resource-id 9876543210 \
#     --app-id my-research-app_1234567890 \
#     --engine-location us-central1 \
#     --location global \
#     --display-name "Clinical Research Synthesizer" \
#     --description "AI agent for medical literature synthesis" \
#     --icon-uri "https://example.com/icon.png"
#
# List all agents registered in the Gemini Enterprise app:
#   ./deployment/deploy_to_gemini_enterprise.sh --list
#
# Update an existing agent (uses GEMINI_ENTERPRISE_AGENT_ID from .env):
#   ./deployment/deploy_to_gemini_enterprise.sh --update
#
# Update with explicit agent ID:
#   ./deployment/deploy_to_gemini_enterprise.sh --update --agent-id AGENT_ID
#
# Delete an agent from Gemini Enterprise:
#   ./deployment/deploy_to_gemini_enterprise.sh --delete --agent-id AGENT_ID
#
# Show help:
#   ./deployment/deploy_to_gemini_enterprise.sh --help
#
# ============================================================================
# END-TO-END WORKFLOW
# ============================================================================
#
# Step 1: Deploy to Agent Engine
#   ./deployment/setup_and_deploy.sh
#   # Output: "Created remote agent: projects/.../reasoningEngines/RESOURCE_ID"
#
# Step 2: Add to .env
#   echo 'AGENT_ENGINE_RESOURCE_ID="RESOURCE_ID"' >> .env
#   echo 'GEMINI_ENTERPRISE_APP_ID="YOUR_APP_ID"' >> .env
#
# Step 3: Register with Gemini Enterprise
#   ./deployment/deploy_to_gemini_enterprise.sh --register
#   # Output: Saves GEMINI_ENTERPRISE_AGENT_ID to .env automatically
#
# Step 4: Verify in console
#   https://console.cloud.google.com/gen-app-builder/engines?project=PROJECT_ID
#
# ============================================================================
# NOTES
# ============================================================================
#
# - The Discovery Engine API requires the numeric PROJECT_NUMBER in the URL,
#   not the project ID. The script auto-resolves this if not set.
#
# - Agent Engine location (regional, e.g. us-central1) and Gemini Enterprise
#   location (multi-region, e.g. global) are separate. See the location
#   mapping table:
#     Gemini Enterprise "global" -> Any Agent Engine region
#     Gemini Enterprise "us"     -> us-central1, us-east1, us-west1
#     Gemini Enterprise "eu"     -> europe-west1, europe-west2, europe-central2
#
# - On success, the script saves GEMINI_ENTERPRISE_AGENT_ID to .env for use
#   in subsequent --update and --delete commands.
#
# - Model Armor, when enabled in Gemini Enterprise, does NOT protect
#   conversations with registered ADK agents.
#
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
fail()  { error "$*"; exit 1; }

# ── Parse flags ──────────────────────────────────────────────────────────────
ACTION=""
FLAG_AGENT_ID=""
FLAG_PROJECT=""
FLAG_PROJECT_NUMBER=""
FLAG_APP_ID=""
FLAG_RESOURCE_ID=""
FLAG_LOCATION=""
FLAG_ENGINE_LOCATION=""
FLAG_DISPLAY_NAME=""
FLAG_DESCRIPTION=""
FLAG_ICON_URI=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --register)         ACTION="register"; shift ;;
        --list)             ACTION="list"; shift ;;
        --delete)           ACTION="delete"; shift ;;
        --update)           ACTION="update"; shift ;;
        --agent-id)         FLAG_AGENT_ID="$2"; shift 2 ;;
        --project)          FLAG_PROJECT="$2"; shift 2 ;;
        --project-number)   FLAG_PROJECT_NUMBER="$2"; shift 2 ;;
        --app-id)           FLAG_APP_ID="$2"; shift 2 ;;
        --resource-id)      FLAG_RESOURCE_ID="$2"; shift 2 ;;
        --location)         FLAG_LOCATION="$2"; shift 2 ;;
        --engine-location)  FLAG_ENGINE_LOCATION="$2"; shift 2 ;;
        --display-name)     FLAG_DISPLAY_NAME="$2"; shift 2 ;;
        --description)      FLAG_DESCRIPTION="$2"; shift 2 ;;
        --icon-uri)         FLAG_ICON_URI="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 ACTION [OPTIONS]"
            echo ""
            echo "Actions:"
            echo "  --register               Register agent with Gemini Enterprise"
            echo "  --list                    List registered agents"
            echo "  --update                  Update an existing agent"
            echo "  --delete                  Delete an agent from Gemini Enterprise"
            echo ""
            echo "Options:"
            echo "  --agent-id <ID>           Agent ID (required for --delete, --update)"
            echo "  --project <PROJECT>       GCP project ID (or GOOGLE_CLOUD_PROJECT)"
            echo "  --project-number <NUM>    GCP project number (or GOOGLE_CLOUD_PROJECT_NUMBER)"
            echo "  --app-id <APP_ID>         Gemini Enterprise app ID (or GEMINI_ENTERPRISE_APP_ID)"
            echo "  --resource-id <ID>        Agent Engine resource ID (or AGENT_ENGINE_RESOURCE_ID)"
            echo "  --location <LOC>          Discovery Engine location: global|us|eu (default: global)"
            echo "  --engine-location <LOC>   Agent Engine region (default: us-central1)"
            echo "  --display-name <NAME>     Agent display name"
            echo "  --description <DESC>      Agent description"
            echo "  --icon-uri <URI>          Public URI for agent icon"
            echo "  -h, --help                Show this help"
            exit 0
            ;;
        *) fail "Unknown option: $1" ;;
    esac
done

[[ -n "$ACTION" ]] || fail "No action specified. Use --register, --list, --update, or --delete."

# ── Load .env ────────────────────────────────────────────────────────────────
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# ── Resolve parameters ───────────────────────────────────────────────────────
PROJECT_ID="${FLAG_PROJECT:-${GOOGLE_CLOUD_PROJECT:-}}"
PROJECT_NUMBER="${FLAG_PROJECT_NUMBER:-${GOOGLE_CLOUD_PROJECT_NUMBER:-}}"
APP_ID="${FLAG_APP_ID:-${GEMINI_ENTERPRISE_APP_ID:-}}"
RESOURCE_ID="${FLAG_RESOURCE_ID:-${AGENT_ENGINE_RESOURCE_ID:-}}"
GE_LOCATION="${FLAG_LOCATION:-${GEMINI_ENTERPRISE_LOCATION:-global}}"
ENGINE_LOCATION="${FLAG_ENGINE_LOCATION:-${AGENT_ENGINE_LOCATION:-us-central1}}"
DISPLAY_NAME="${FLAG_DISPLAY_NAME:-${AGENT_DISPLAY_NAME:-Clinical Research Synthesizer}}"
DESCRIPTION="${FLAG_DESCRIPTION:-${AGENT_DESCRIPTION:-AI research agent that synthesizes scientific literature and clinical trial data using MedGemma.}}"
ICON_URI="${FLAG_ICON_URI:-${AGENT_ICON_URI:-https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/science/default/24px.svg}}"
AGENT_ID="${FLAG_AGENT_ID:-${GEMINI_ENTERPRISE_AGENT_ID:-}}"

# ── Helper: auto-resolve project number ──────────────────────────────────────
resolve_project_number() {
    if [[ -z "$PROJECT_NUMBER" ]]; then
        info "Resolving project number for $PROJECT_ID..."
        PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" \
            --format="value(projectNumber)" 2>/dev/null || true)
        if [[ -z "$PROJECT_NUMBER" ]]; then
            fail "Could not resolve project number. Set GOOGLE_CLOUD_PROJECT_NUMBER in .env or use --project-number."
        fi
        ok "Project number: $PROJECT_NUMBER"
        save_env "GOOGLE_CLOUD_PROJECT_NUMBER" "$PROJECT_NUMBER"
    fi
}

# ── Discovery Engine API URL ─────────────────────────────────────────────────
# The API uses the project NUMBER (not ID) in the URL path.
DISCOVERY_ENGINE_API="https://discoveryengine.googleapis.com"

build_base_url() {
    echo "${DISCOVERY_ENGINE_API}/v1alpha/projects/${PROJECT_NUMBER}/locations/${GE_LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
}

# ── Validate ─────────────────────────────────────────────────────────────────
validate_common() {
    [[ -n "$PROJECT_ID" ]] || fail "GOOGLE_CLOUD_PROJECT is required. Set in .env or use --project."
    [[ -n "$APP_ID" ]]     || fail "GEMINI_ENTERPRISE_APP_ID is required. Set in .env or use --app-id."

    command -v gcloud >/dev/null 2>&1 || fail "gcloud CLI not found."
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
    [[ -n "$ACTIVE_ACCOUNT" ]] || fail "No active gcloud account. Run: gcloud auth login"

    resolve_project_number
}

validate_register() {
    validate_common
    [[ -n "$RESOURCE_ID" ]] || fail "AGENT_ENGINE_RESOURCE_ID is required. Set in .env or use --resource-id."
}

get_token() {
    gcloud auth print-access-token
}

# ── Enable Discovery Engine API ──────────────────────────────────────────────
ensure_api_enabled() {
    info "Ensuring Discovery Engine API is enabled..."
    gcloud services enable discoveryengine.googleapis.com \
        --project="$PROJECT_ID" --quiet 2>/dev/null
    ok "Discovery Engine API enabled"
}

# ── Save to .env ─────────────────────────────────────────────────────────────
save_env() {
    local key="$1" value="$2"
    if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
        sed -i "s|^${key}=.*|${key}=\"${value}\"|" "$ENV_FILE"
    else
        echo "${key}=\"${value}\"" >> "$ENV_FILE"
    fi
}

# ── Register agent ───────────────────────────────────────────────────────────
register_agent() {
    validate_register
    ensure_api_enabled

    REASONING_ENGINE="projects/${PROJECT_ID}/locations/${ENGINE_LOCATION}/reasoningEngines/${RESOURCE_ID}"
    API_URL=$(build_base_url)

    echo ""
    info "Registering agent with Gemini Enterprise..."
    info "  Project:            $PROJECT_ID ($PROJECT_NUMBER)"
    info "  Gemini Enterprise:  $APP_ID (location: $GE_LOCATION)"
    info "  Agent Engine:       $RESOURCE_ID (location: $ENGINE_LOCATION)"
    info "  Display Name:       $DISPLAY_NAME"
    echo ""

    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST \
        -H "Authorization: Bearer $(get_token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${API_URL}" \
        -d '{
  "displayName": "'"${DISPLAY_NAME}"'",
  "description": "'"${DESCRIPTION}"'",
  "icon": {
    "uri": "'"${ICON_URI}"'"
  },
  "adk_agent_definition": {
    "tool_settings": {
      "toolDescription": "'"${DESCRIPTION}"'"
    },
    "provisioned_reasoning_engine": {
      "reasoningEngine": "'"${REASONING_ENGINE}"'"
    }
  }
}')

    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

    if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
        ok "Agent registered with Gemini Enterprise!"
        echo ""
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

        # Extract and save the agent ID
        REGISTERED_ID=$(echo "$RESPONSE_BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    name = data.get('name', '')
    print(name.split('/')[-1] if name else 'unknown')
except: print('unknown')
" 2>/dev/null)

        echo ""
        ok "Agent ID: $REGISTERED_ID"

        if [[ "$REGISTERED_ID" != "unknown" ]]; then
            save_env "GEMINI_ENTERPRISE_AGENT_ID" "$REGISTERED_ID"
            ok "Saved GEMINI_ENTERPRISE_AGENT_ID to .env"
        fi

        echo ""
        echo "Access in Google Cloud Console:"
        echo "  https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
    else
        error "Registration failed (HTTP $HTTP_CODE):"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
        echo ""
        echo "Common issues:"
        echo "  1. Invalid Agent Engine ID — verify from deploy.py output"
        echo "  2. Invalid Gemini Enterprise App ID — check Gen App Builder console"
        echo "  3. Permissions — ensure you have roles/discoveryengine.admin"
        echo "  4. Agent Engine not ready — wait for deployment to complete"
        exit 1
    fi
}

# ── List agents ──────────────────────────────────────────────────────────────
list_agents() {
    validate_common

    API_URL=$(build_base_url)
    info "Listing agents in Gemini Enterprise app: $APP_ID"

    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET \
        -H "Authorization: Bearer $(get_token)" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${API_URL}")

    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

    if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
        echo ""
        echo "$RESPONSE_BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    agents = data.get('agents', [])
    if not agents:
        print('No agents registered.')
    else:
        for a in agents:
            name = a.get('name', 'N/A')
            agent_id = name.split('/')[-1] if name else 'N/A'
            display = a.get('displayName', 'N/A')
            desc = a.get('description', '')
            print(f'  Agent ID:     {agent_id}')
            print(f'  Display Name: {display}')
            if desc:
                print(f'  Description:  {desc}')
            print(f'  Resource:     {name}')
            print()
except Exception as e:
    print(f'Error parsing response: {e}')
" 2>/dev/null || echo "$RESPONSE_BODY"
    else
        error "List failed (HTTP $HTTP_CODE):"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
        exit 1
    fi
}

# ── Update agent ─────────────────────────────────────────────────────────────
update_agent() {
    validate_register
    [[ -n "$AGENT_ID" ]] || fail "Agent ID is required. Use --agent-id or set GEMINI_ENTERPRISE_AGENT_ID in .env."

    REASONING_ENGINE="projects/${PROJECT_ID}/locations/${ENGINE_LOCATION}/reasoningEngines/${RESOURCE_ID}"
    AGENT_URL="${DISCOVERY_ENGINE_API}/v1alpha/projects/${PROJECT_NUMBER}/locations/${GE_LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_ID}"

    info "Updating agent: $AGENT_ID"

    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PATCH \
        -H "Authorization: Bearer $(get_token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${AGENT_URL}" \
        -d '{
  "displayName": "'"${DISPLAY_NAME}"'",
  "description": "'"${DESCRIPTION}"'",
  "icon": {
    "uri": "'"${ICON_URI}"'"
  },
  "adk_agent_definition": {
    "tool_settings": {
      "toolDescription": "'"${DESCRIPTION}"'"
    },
    "provisioned_reasoning_engine": {
      "reasoningEngine": "'"${REASONING_ENGINE}"'"
    }
  }
}')

    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

    if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
        ok "Agent updated successfully!"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    else
        error "Update failed (HTTP $HTTP_CODE):"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
        exit 1
    fi
}

# ── Delete agent ─────────────────────────────────────────────────────────────
delete_agent() {
    validate_common
    [[ -n "$AGENT_ID" ]] || fail "Agent ID is required. Use --agent-id or set GEMINI_ENTERPRISE_AGENT_ID in .env."

    AGENT_URL="${DISCOVERY_ENGINE_API}/v1alpha/projects/${PROJECT_NUMBER}/locations/${GE_LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_ID}"

    info "Deleting agent: $AGENT_ID from Gemini Enterprise app: $APP_ID"

    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE \
        -H "Authorization: Bearer $(get_token)" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${AGENT_URL}")

    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

    if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
        ok "Agent $AGENT_ID deleted from Gemini Enterprise."
    else
        error "Delete failed (HTTP $HTTP_CODE):"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
        exit 1
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
echo ""
echo "=============================================="
echo "  Gemini Enterprise — Agent Registration"
echo "=============================================="
echo ""

case "$ACTION" in
    register) register_agent ;;
    list)     list_agents ;;
    update)   update_agent ;;
    delete)   delete_agent ;;
    *)        fail "Unknown action: $ACTION" ;;
esac
