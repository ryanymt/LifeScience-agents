# Medical Research Agent

**Medical Research Agent** is a sophisticated AI agent designed to assist with medical research queries. This project implements a robust, multi-agent system using the ADK framework and Google Cloud's Vertex AI.

The agent can answer general medical questions and perform specialized analysis on chemical compounds. It uses a multi-agent architecture, routing queries to the appropriate specialized model.

**Problem it Solves**: It addresses the challenge of accessing and interpreting different types of medical and scientific information, from general medical knowledge to specific biochemical predictions.

**How it Can be Expanded**: Its modular design allows for easy expansion. New specialists can be added to connect to more data sources (e.g., proteomics databases, clinical trial information) or to perform more advanced analyses, such as predicting protein folding or summarizing the latest research papers.

### Key Capabilities
* **General Medical Questions:** Powered by MedGemma for answering a wide range of medical questions.
* **Chemical Compound Analysis:** Utilizes TxGemma for technical analysis, such as predicting whether a molecule will cross the blood-brain barrier based on its SMILES string.
* **Intelligent Routing:** A coordinator agent analyzes the user's query and routes it to the appropriate specialist sub-agent.

<img width="1446" height="763" alt="agent_architecture" src="https://github.com/user-attachments/assets/f9542abe-aeef-4e05-b5df-f14461df8edf" />

---

## Setup and Installation

### Prerequisites

Before you begin, ensure you have the following set up:

1.  **Google Cloud Project**: A Google Cloud project with billing enabled and the **Vertex AI API** enabled.
2.  **Model Endpoints (Crucial Step)**: You must deploy the `TxGemma` and `MedGemma` models from the **Vertex AI Model Garden** to **Vertex AI Endpoints**.
    * **Copy the Endpoint IDs for both models.**
3.  **Authentication**: Authenticate your local environment with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```
4.  **Python & Poetry**: Python 3.11+ and [Poetry](https://python-poetry.org/docs/#installation) for managing dependencies.

### Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/ryanymt/LifeScience-agents.git](https://github.com/ryanymt/LifeScience-agents.git)
    cd LifeScience-agents/medical-research
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

    # The Endpoint IDs for your deployed models
    TXGEMMA_ENDPOINT_ID="your-txgemma-endpoint-id"
    MEDGEMMA_ENDPOINT_ID="your-medgemma-endpoint-id"
    ```

---

## Usage

### Local Testing

You can interact with the agent locally using the `adk run` command. This is perfect for testing and debugging.

**Run with a medical question:**
```bash
poetry run adk run medical_research/ "What are the symptoms of high blood pressure?"
```

# Agent Demo Video
- Main agent (Gemini) routing patient diagnosis query (with medical history, symptom, early examination findings, lab test results, and challanges) to Medical Search Agent (MedGemma) and suggest diagnosis tests. 
- Main agent (Gemini) routing molecule SMILE string query to Medical Analyst (TxGemma) to answer the question.

https://github.com/user-attachments/assets/90ce62ac-9c77-46c1-9567-b0e671ffa56c

