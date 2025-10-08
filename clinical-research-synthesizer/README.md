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

Before you begin, ensure you have the following set up:

1.  **Google Cloud Project**: A Google Cloud project with billing enabled and the **Vertex AI API** enabled.
2.  **MedGemma Model Endpoint (Crucial Step)**: You must deploy the google/medgemma-1.0 model from the **Vertex AI Model Garden** to a **Vertex AI Endpoint**.
    * **Copy the Endpoint ID.**
3.  **Authentication**: Authenticate your local environment with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```
4.  **Python & Poetry**: Python 3.11+ and [Poetry](https://python-poetry.org/docs/#installation) for managing dependencies.

### Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/ryanymt/LifeScience-agents.git
    cd clinical-research-synthesizer
    ```

2.  **Install Dependencies**:
    ```bash
    poetry install
    ```

3.  **Configure Environment Variables**:
    Create a `.env` file by copying the example template:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and fill in the required values with your specific project details and the Endpoint IDs you copied during the prerequisite step.
    ```env
    # .env - Local Environment Variables
    GOOGLE_CLOUD_PROJECT="gcp-project-id"
    GOOGLE_CLOUD_LOCATION="gcp-region" # e.g., us-central1
    GOOGLE_CLOUD_STORAGE_BUCKET="gcs-bucket-for-staging"
    GOOGLE_GENAI_USE_VERTEXAI="true"

    # The Endpoint ID for your deployed MedGemma model
    MEDGEMMA_ENDPOINT_ID="medgemma-endpoint-id"

    ```

---

## Usage

### Local Testing

You can interact with the agent locally using the `adk run` command. This is perfect for testing and debugging.

**Basic Run:**
```bash
poetry run adk run clinical_research_synthesizer/ "Summarize the latest research on the use of Lecanemab for early Alzheimer's disease. What are the common pre-conditions and exclusion criteria for patients in its clinical trials, particularly regarding cerebral amyloid angiopathy?"
```
This will take a few minutes as it'll need to iterate a few papers and trails results. 


### Deployment to Vertex AI Agent Engine

This project includes a script to deploy the agent to a scalable, serverless environment on Vertex AI.

**Create a New Agent:**
This command packages your code and deploys it as a new Agent Engine.
```bash
poetry run python deployment/deploy.py --create
```

**List Deployed Agents:**
```bash
poetry run python deployment/deploy.py --list
```

**Delete an Agent:**
You will need the `resource_id` from the list command.
```bash
poetry run python deployment/deploy.py --delete --resource_id="your-agent-resource-id"
```

---

## Project Structure

The agent uses a hierarchical design:

* **`research_coordinator` (Main Agent)**: The "brain" of the operation. It analyzes user queries, creates a multi-step plan, and delegates tasks.
* **`specialists/` (Sub-Agents)**:
    * **`literature_researcher`**: A specialist for all literature research tasks, including finding papers, extracting text, and summarizing with MedGemma.
    * **`clinical_trial_specialist`**: A specialist for finding and extracting information from clinical trials.
    * **`search_specialist`**: A specialist for performing general Google searches to find PDF URLs.

This modular structure makes the agent easy to maintain and extend with new tools and capabilities.

----
## Agent Usage
Google AgentSpace is used for the demo. 

Own front-end UI can be built and call Agent engine's Agent API. (might try to add that frontend UI later)



------
## Demo Video Walkthrough



https://github.com/user-attachments/assets/0380c72d-ace9-4d66-9189-8edcccd1bb86


