# Medical Research Agent

## Overview

***Ignore Frontend-UI for the moment
(notes: this is work in progress. agents are built and tested individually before putting things together. Some codes are to be cleaned up)

This AI-driven agent is designed to assist with medical research queries. It can answer general medical questions and perform specialized analysis on chemical compounds. The agent uses a multi-agent architecture, routing queries to the appropriate specialized model.

- **Medical Search**: Powered by MedGemma for general medical questions.
- **Medical Analyst**: Powered by TxGemma for technical analysis, such as predicting blood-brain barrier crossing from a SMILES string.

  <img width="1446" height="763" alt="agent_architecture" src="https://github.com/user-attachments/assets/f9542abe-aeef-4e05-b5df-f14461df8edf" />


## Deployment to Vertex AI Agent Engine

### Prerequisites

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.11+
    *   Poetry
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [Poetry website](https://python-poetry.org/docs/) for installation.

        ```bash
        pip install poetry
        ```

    * A project on Google Cloud Platform
    * Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation**

    ```bash
    # Clone this repository.
    git clone https://github.com/ryanymt/LifeScience-agents
    cd LifeScience-agents/medical-research
    # Install the package and dependencies.
    poetry install
    ```

- A configured Google Cloud project.
- The Google Cloud CLI authenticated (`gcloud auth application-default login`).
- A `.env` file in the root directory with your `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `GOOGLE_CLOUD_STORAGE_BUCKET`. 
- Deploy TxGemma and MedGemma endpoints from Vertex AI > Model Garden. Note down the endpoint IDs and update in .env file . Sub-agents are written to align with TxGemma and MedGemma returns strings. 

    *   Authenticate your Google Cloud account.

        ```bash
        gcloud auth application-default login
        ```


Move in the root directory and run adk test

```bash
adk run medical_research
```

Or on a web interface:

```bash
 adk web
```

### Deploying the Agent

To create and deploy the agent, run the following command:

```bash
poetry run python deployment/deploy.py --create
```

# Agent Demo Video
- Main agent (Gemini) routing patient diagnosis query (with medical history, symptom, early examination findings, lab test results, and challanges) to Medical Search Agent (MedGemma) and suggest diagnosis tests. 
- Main agent (Gemini) routing molecule SMILE string query to Medical Analyst (TxGemma) to answer the question.


https://github.com/user-attachments/assets/90ce62ac-9c77-46c1-9567-b0e671ffa56c


