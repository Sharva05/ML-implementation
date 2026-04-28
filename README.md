# Network Log Analysis ML Pipeline

This project is a comprehensive Machine Learning pipeline for network log analysis. It covers the full lifecycle from data ingestion to anomaly detection, correlation, log importance scoring, data storage, and visualization.

## Architecture & Modules

The project is structured into logical modules reflecting the steps in the ML pipeline:

- **`data/`**: Directory for storing raw and processed datasets.
- **`ingestion/`**: Data ingestion processes to bring in network logs.
- **`parsing/`**: Parsers to convert raw log lines into structured data formats.
- **`features/`**: Feature engineering logic to transform parsed data into model-ready features.
- **`ml/`**: Machine Learning models specifically built for detecting anomalies in log data.
- **`correlation/`**: Logic to identify correlations between different log events and anomalies.
- **`scoring/`**: Mechanisms to compute an "importance score" for log events to prioritize review.
- **`storage/`**: Interfaces for data persistence, interacting with PostgreSQL and Elasticsearch.
- **`visualization/`**: Configurations and instructions for dashboarding via Kibana and Grafana.
- **`evaluation/`**: Contains scripts and utilities for evaluating model and pipeline performance.
- **`pipeline.py`**: The central orchestrator script that ties the modules together.

## Infrastructure Setup

To run the pipeline infrastructure, we use Docker Compose to spin up the required databases and visualization tools.

### 1. Configure Environment Variables

First, set up your local environment variables by copying the provided example file:

```bash
cp .env.example .env
```

Open `.env` and configure your credentials. You can also customize the PostgreSQL port (`POSTGRES_PORT`) if the default `5432` is already in use on your machine.

### 2. Start the Services

Once your `.env` is ready, deploy the infrastructure stack:

```bash
docker compose up -d
```

This command will spin up the following containers:
- **PostgreSQL** (Relational data storage)
- **Elasticsearch** (Log storage and search)
- **Kibana** (Elasticsearch visualization, mapped to port `5601`)
- **Grafana** (General metrics visualization, mapped to port `3000`)

### 3. Verify the Deployment

Ensure all services are up and running:

```bash
docker ps
```
You should see `log_postgres`, `log_elasticsearch`, `log_kibana`, and `log_grafana` in the output.
