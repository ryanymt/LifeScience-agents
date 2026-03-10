# Clinical Research Synthesizer

**Clinical Research Synthesizer** is a sophisticated AI agent designed to accelerate early-stage clinical research workflows. This project implements a robust, multi-agent system using the ADK framework and Google Cloud's Vertex AI.

The agent can perform complex, multi-step research tasks by decomposing a user's query into a logical plan and delegating tasks to its specialized sub-agents.

**Problem it Solves**: It addresses the slow, manual process of gathering and making sense of information from disconnected sources like scientific literature (PubMed), clinical trial data (ClinicalTrials.gov).

**How it Can be Expanded**: Its modular design allows for easy expansion. New specialists can be added to connect to more data sources (e.g., genomics databases, internal company data) or to perform more advanced analyses, such as predicting drug-protein interactions or summarizing regulatory documents.

### Key Capabilities
* **Literature Research:** Performs deep searches of the PubMed database to find relevant scientific articles for therapeutic context.

* **Full-Text Analysis:** Extracts and summarizes the full text of scientific papers from PDF URLs.

* **Clinical Trial Search:** Finds relevant clinical trials on ClinicalTrials.gov.

* **Eligibility Criteria Extraction:** Extracts and parses inclusion and exclusion criteria from clinical trials.

* **Transparent Reasoning:** The agent explicitly states its execution plan, allowing users to see its step-by-step reasoning process.


<img width="1365" height="761" alt="LifeScience Diagrams - Page 3 (2)" src="https://github.com/user-attachments/assets/cc3abc75-b71e-41b5-aa6e-f538f56f6fce" />



---

## Setup and Installation

### Prerequisites

1. **Google Cloud Project** with billing enabled.
2. **gcloud CLI** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Python 3.11+** and [Poetry](https://python-poetry.org/docs/#installation).

### Option A: One-Click Setup (Recommended)

The setup script handles everything — API enablement, bucket creation, MedGemma deployment, and agent deployment:

```bash
git clone https://github.com/ryanymt/LifeScience-agents.git
cd LifeScience-agents/clinical-research-synthesizer
./deployment/setup_and_deploy.sh
```

This will:
1. Validate prerequisites (gcloud auth, Python, Poetry)
2. Configure and save project settings to `.env`
3. Enable Vertex AI and Cloud Storage APIs
4. Create a GCS staging bucket
5. Deploy MedGemma 27B to a Vertex AI endpoint (takes 10-20 min)
6. Install Python dependencies
7. Deploy the agent to Vertex AI Agent Engine

**Script flags:**
```bash
./deployment/setup_and_deploy.sh --skip-medgemma   # Skip MedGemma if already deployed
./deployment/setup_and_deploy.sh --agent-only       # Only deploy the agent (skip setup)
./deployment/setup_and_deploy.sh --list             # List deployed agents
./deployment/setup_and_deploy.sh --delete <ID>      # Delete a deployed agent
```

### Option B: Manual Setup

1. **Clone and install:**
   ```bash
   git clone https://github.com/ryanymt/LifeScience-agents.git
   cd LifeScience-agents/clinical-research-synthesizer
   poetry install
   ```

2. **Deploy MedGemma** (requires A100 GPU quota in us-central1):
   ```bash
   poetry run python deployment/deploy_medgemma.py          # Spot instance (cheaper)
   poetry run python deployment/deploy_medgemma.py --nospot  # On-demand instance
   ```
   The script auto-saves the endpoint ID to `.env`. See `deploy_medgemma.py` for
   MedGemma 1.5 4B deployment instructions.

3. **Configure `.env`:**
   ```env
   GOOGLE_CLOUD_PROJECT="your-project-id"
   GOOGLE_CLOUD_LOCATION="global"
   GOOGLE_GENAI_USE_VERTEXAI="true"
   MEDGEMMA_ENDPOINT_ID="your-medgemma-endpoint-id"
   MEDGEMMA_LOCATION="us-central1"
   ```

---

## Usage

### Local Testing

Test the agent locally using `adk run`:

```bash
poetry run adk run clinical_research_synthesizer/
```

This starts an interactive session. Example queries:

```
summarize paper Lecanemab in Early Alzheimer's Disease
```

```
run literature research on CAR-T cell therapy for solid tumors
```

```
run clinical trial search on pembrolizumab melanoma
```

```
Summarize the latest research on the use of Lecanemab for early Alzheimer's disease.
What are the common pre-conditions and exclusion criteria for patients in its clinical
trials, particularly regarding cerebral amyloid angiopathy?
```

General research questions will trigger the full autonomous workflow — the agent plans
its approach, searches literature, summarizes papers with MedGemma, finds clinical
trials, and synthesizes a final report.

### Testing with ADK Web UI

You can also test with the ADK web interface:

```bash
poetry run adk web clinical_research_synthesizer/
```

---

## Deployment

### Step 1: Deploy to Vertex AI Agent Engine

This deploys the agent as a managed, scalable endpoint on Vertex AI.

**Using the setup script (recommended):**
```bash
./deployment/setup_and_deploy.sh
```

**Or directly with deploy.py:**
```bash
poetry run python deployment/deploy.py --create
```

**Manage deployed agents:**
```bash
poetry run python deployment/deploy.py --list
poetry run python deployment/deploy.py --delete --resource_id="RESOURCE_ID"
```

Note the reasoning engine resource ID from the output — you'll need it for the next step.

### Step 2: Register with Gemini Enterprise

Once the agent is deployed to Agent Engine, register it with Gemini Enterprise
(formerly AgentSpace) to make it available to end users via the Gemini Enterprise
web app.

**Prerequisites:**
- A Gemini Enterprise app created in the [Google Cloud console](https://console.cloud.google.com/gen-app-builder/engines)
- `roles/discoveryengine.admin` IAM role

**Add these to your `.env`:**
```env
AGENT_ENGINE_RESOURCE_ID="1234567890"
GEMINI_ENTERPRISE_APP_ID="your-app-id"
# GOOGLE_CLOUD_PROJECT_NUMBER is auto-resolved if not set
```

**Register the agent:**
```bash
./deployment/deploy_to_gemini_enterprise.sh --register
```

**Manage registered agents:**
```bash
./deployment/deploy_to_gemini_enterprise.sh --list
./deployment/deploy_to_gemini_enterprise.sh --update --agent-id AGENT_ID
./deployment/deploy_to_gemini_enterprise.sh --delete --agent-id AGENT_ID
```

All parameters can be passed as flags instead of env vars. Run with `--help` for details.

### MedGemma Endpoint Management

**List available deployment options:**
```bash
poetry run python deployment/deploy_medgemma.py --list_options
```

**Undeploy MedGemma (stop billing):**
```bash
poetry run python deployment/deploy_medgemma.py --undeploy
```

---

## Project Structure

The agent uses a hierarchical multi-agent design:

* **`research_coordinator` (Main Agent)**: The orchestrator. It analyzes user queries, creates a multi-step plan, and delegates tasks to specialists. Uses Gemini 3.1 Pro.
* **`specialists/` (Sub-Agents)**:
    * **`literature_researcher`**: Searches PubMed for papers, retrieves full text from PubMed Central, and summarizes using MedGemma 27B. Uses Gemini 3.1 Pro.
    * **`clinical_trial_specialist`**: Finds and extracts information from ClinicalTrials.gov. Uses Gemini 3.1 Pro.
    * **`search_specialist`**: Performs PubMed Central full-text retrieval. Uses Gemini 3 Flash.

**Key design decisions:**
- Full paper text stays within the `literature_researcher` specialist and is processed by MedGemma — it never flows through the coordinator, saving Gemini token quota.
- Gemini 3.x models use the `global` endpoint; MedGemma uses a regional endpoint (`us-central1`).
- MedGemma 1.0 27B is used for structured paper summarization (Introduction, Methods, Results, Conclusion, Key Snippets).

```
clinical_research_synthesizer/
├── agent.py                          # Root agent (research_coordinator)
├── prompt.py                         # Coordinator system prompt
└── specialists/
    ├── literature_researcher/
    │   ├── agent.py                  # Literature researcher agent
    │   ├── prompt.py
    │   └── tools/
    │       ├── fetch_articles.py     # PubMed search
    │       ├── extract_text_from_pdf.py
    │       └── summarize_paper_with_medgemma.py  # MedGemma integration
    ├── clinical_trial_specialist/
    │   ├── agent.py
    │   ├── prompt.py
    │   └── tools/
    │       ├── search_trials.py      # ClinicalTrials.gov search
    │       └── extract_criteria.py
    └── search_specialist/
        ├── agent.py
        ├── prompt.py
        └── tools/
            └── pmc_search.py         # PubMed Central full-text retrieval

deployment/
├── setup_and_deploy.sh               # One-click full setup & deploy
├── deploy.py                         # Agent Engine deployment
├── deploy_medgemma.py                # MedGemma model deployment
└── deploy_to_gemini_enterprise.sh    # Gemini Enterprise registration
```

---

## Agent Access

Once deployed, the agent can be accessed via:

1. **Gemini Enterprise** — Register using `deploy_to_gemini_enterprise.sh` for end-user access through the Gemini Enterprise web app.
2. **Agent Engine API** — Build a custom front-end and call the Agent Engine API directly.
3. **Local testing** — Use `adk run` or `adk web` for development and debugging.



------
## Demo Video Walkthrough



https://github.com/user-attachments/assets/0380c72d-ace9-4d66-9189-8edcccd1bb86


