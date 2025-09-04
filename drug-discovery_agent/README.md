# Agentic-Tx: A Drug Discovery Research Agent
(Demo recording at the end of the README)

<img width="1140" height="850" alt="LifeScience Diagrams - Page 2 (1)" src="https://github.com/user-attachments/assets/89d3adfd-e794-4ee1-b152-227f7958cb8d" />



**Agentic-Tx** is a sophisticated AI agent designed to accelerate early-stage drug discovery workflows. Evolving from the concepts demonstrated in the original [TxGemma Agentic Demo notebook](https://github.com/google-gemini/gemma-cookbook/blob/main/TxGemma/%5BTxGemma%5DAgentic_Demo_with_Hugging_Face.ipynb), this project implements a robust, multi-agent system using the ADK framework and Google Cloud's Vertex AI.

The agent can perform complex, multi-step research tasks by decomposing a user's query into a logical plan and delegating tasks to its specialized sub-agents.

### Key Capabilities
* **Compound Identification**: Looks up chemical compounds from SMILES strings using the PubChem database to retrieve their common names and properties.
* **Toxicity Prediction**: Utilizes a deployed TxGemma `predict` model to assess the clinical toxicity of a compound.
* **Literature Research**: Performs deep searches of the PubMed database to find relevant scientific articles for therapeutic context.
* **General Knowledge Q&A**: Answers general therapeutic questions using a deployed TxGemma `chat` model.
* **Transparent Reasoning**: The agent explicitly states its execution plan, allowing users to see its step-by-step reasoning process.

---

## Setup and Installation

### Prerequisites

Before you begin, ensure you have the following set up:

1.  **Google Cloud Project**: A Google Cloud project with billing enabled and the **Vertex AI API** enabled.
2.  **TxGemma Model Endpoints (Crucial Step)**: You must deploy two TxGemma models from the Hugging Face Hub to two separate **Vertex AI Endpoints**.
    * **Predict Model**: Deploy `google/txgemma-9b-predict` (or another predict variant). **Copy the Endpoint ID**.
    * **Chat Model**: Deploy `google/txgemma-9b-chat` (or another chat variant). **Copy the Endpoint ID**.
3.  **Authentication**: Authenticate your local environment with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```
4.  **Python & Poetry**: Python 3.11+ and [Poetry](https://python-poetry.org/docs/#installation) for managing dependencies.

### Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/ryanymt/LifeScience-agents.git
    cd drug-discovery_agent
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

    # The Endpoint IDs for your deployed TxGemma models
    TXGEMMA_PREDICT_ENDPOINT_ID="txgemma-predict-endpoint-id"
    TXGEMMA_CHAT_ENDPOINT_ID="txgemma-chat-endpoint-id"
    ```

---

## Usage

### Local Testing

You can interact with the agent locally using the `adk run` command. This is perfect for testing and debugging.

**Basic Run:**
```bash
poetry run adk run "What is the common name for the compound with SMILES CC(=O)OC1=CC=CC=C1C(=O)O ?"
```

**Comprehensive Analysis Example:**
To test the full multi-step workflow, use the complex comparative query. The agent will respond with its execution plan followed by the detailed analysis.
```bash
poetry run adk run "Which of the following drugs is preferred for further development? 1. CC(=O)OC1=CC=CC=C1C(=O)O or 2. O=C(CCCCCCC(=O)Nc1ccccc1)NO"
```

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

* **`discovery_coordinator` (Main Agent)**: The "brain" of the operation. It analyzes user queries, creates a multi-step plan, and delegates tasks.
* **`specialists/` (Sub-Agents)**:
    * **`compound_analyzer`**: A specialist for all technical analyses of chemical compounds (identification via PubChem, toxicity prediction).
    * **`literature_researcher`**: A specialist for retrieving information from external knowledge bases (searching PubMed, general Q&A).

This modular structure makes the agent easy to maintain and extend with new tools and capabilities.

----
## Agent Usage
Google AgentSpace is used for the demo. 

<<<<<<< HEAD
Own front-end UI can be built and call Agent engine's Agent API. (might try to add that frontend UI later)
=======
Own front-end UI can be built and call Agent engine's Agent API. (might try to add that frontend UI later)


https://github.com/user-attachments/assets/c3692adb-27a6-4c97-a460-8c3f059b1c2f





>>>>>>> 4cc6ddda01aa13936bb42c7150f657f153e28de6
