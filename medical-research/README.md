# Medical Research Agent

## Overview

This AI-driven agent is designed to assist with medical research queries. It can answer general medical questions and perform specialized analysis on chemical compounds. The agent uses a multi-agent architecture, routing queries to the appropriate specialized model.

- **Medical Search**: Powered by MedGemma for general medical questions.
- **Medical Analyst**: Powered by TxGemma for technical analysis, such as predicting blood-brain barrier crossing from a SMILES string.

## Deployment to Vertex AI Agent Engine

### Prerequisites

- A configured Google Cloud project.
- The Google Cloud CLI authenticated (`gcloud auth application-default login`).
- A `.env` file in the root directory with your `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `GOOGLE_CLOUD_STORAGE_BUCKET`. 
- TxGemma and MedGemma endpoints are used in this demo code

### Deploying the Agent

To create and deploy the agent, run the following command:

```bash
poetry run python deployment/deploy.py --create