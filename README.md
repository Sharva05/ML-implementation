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

### 1. Setup Virtual Environment and Dependencies

Create a virtual environment and install the required libraries:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Set up your local environment variables:

```bash
cp .env.example .env
```

### 3. Start the Services

Deploy the infrastructure stack:

```bash
docker compose up -d
```

### 4. Running Scripts

To avoid import errors, **always run scripts from the project root** using the `-m` (module) flag:

```bash
python3 -m storage.db_writer
```

## Environment Variable Handling

All environment variables must be accessed using the global environment handler via `common.config`.

### Usage

```python
# Variables are lazily evaluated. They are only checked when actually imported/used.
from common.config import DB_URL
```

### Behavior

- **Lazy Evaluation**: Fails only when a specific variable is accessed.
- **Clean Errors**: If a variable is missing, the app outputs a clear message and exits without a long traceback:
  `❌ [ENV ERROR] Missing required variable: NAME`

## Rules

- Do not use `os.getenv()` or `dotenv` directly.
- Always import variables from `common.config`.
- Never print raw environment variables to the console.