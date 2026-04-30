CREATE TABLE logs (
    log_id TEXT PRIMARY KEY,
    sequence_number BIGINT,
    timestamp TIMESTAMP,
    source_type VARCHAR(100),
    service VARCHAR(100),
    host VARCHAR(100),
    log_level VARCHAR(50),
    event_type VARCHAR(100),
    event_action VARCHAR(100),
    template_id VARCHAR(100),
    message TEXT,
    metadata JSONB,
    session_id TEXT
);

CREATE TABLE features (
    log_id TEXT PRIMARY KEY REFERENCES logs(log_id),
    frequency INT,
    event_weight FLOAT,
    frequency_score DOUBLE PRECISION,
    severity_weight DOUBLE PRECISION,
    counter_proximity DOUBLE PRECISION
);

CREATE TABLE anomalies (
    log_id TEXT PRIMARY KEY REFERENCES logs(log_id),
    isolation_score DOUBLE PRECISION,
    zscore DOUBLE PRECISION,
    is_anomaly BOOLEAN
);

CREATE TABLE scores (
    log_id TEXT PRIMARY KEY REFERENCES logs(log_id),
    importance_score FLOAT,
    final_score DOUBLE PRECISION,
    label TEXT,
    correlation_id VARCHAR(100),
    incident_id TEXT,
    is_root_cause BOOLEAN
);

CREATE TABLE incidents (
    incident_id TEXT PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    root_cause_log_id TEXT REFERENCES logs(log_id),
    severity TEXT
);