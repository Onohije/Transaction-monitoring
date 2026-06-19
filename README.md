# Bank Transaction Monitoring Dashboard

A containerized banking operations dashboard for monitoring transaction status, failed-transaction thresholds, audit logs, and service health.

## Architecture

- `api`: FastAPI service with PostgreSQL persistence, transaction simulation, alerts, audit logs, health, and Prometheus metrics.
- `web`: React dashboard served by Nginx.
- `db`: PostgreSQL for ACID-compliant transaction, status history, alert, and log storage.
- `prometheus`: Metrics scraper for API health and operational signals.

## Core Banking Model

Transactions are tracked through a simple operational lifecycle:

`RECEIVED -> VALIDATED -> POSTED -> SETTLED`

Failure states are persisted with reason codes:

- `VALIDATION_FAILED`
- `INSUFFICIENT_FUNDS`
- `HOST_TIMEOUT`
- `REVERSAL_REQUIRED`
- `DUPLICATE_REFERENCE`

Every transaction update creates a status history row and an audit log row.

## Quick Start

```bash
docker compose up --build
```

Open:

- Dashboard: http://localhost:8080
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090

For a teachable build path using Docker, GitHub Actions, and Azure DevOps, read [docs/build-and-run.md](docs/build-and-run.md).

## Configuration

Key API environment variables:

- `DATABASE_URL`: PostgreSQL SQLAlchemy URL.
- `FAILED_TX_THRESHOLD`: number of failed transactions allowed inside the window before an alert is raised.
- `FAILED_TX_WINDOW_SECONDS`: rolling alert window.
- `SIM_FAILURE_RATE`: default failure rate for generated transactions.

## Useful API Endpoints

- `POST /simulate`: create simulated banking transactions.
- `GET /transactions`: query transaction records.
- `GET /transactions/{id}`: transaction details and status history.
- `GET /alerts`: failed transaction threshold alerts.
- `GET /logs`: audit and operational logs.
- `GET /health`: service health.
- `GET /metrics`: Prometheus metrics.

## DevOps

- Docker Compose provides consistent local runtime.
- GitHub Actions runs API tests, frontend build, image build checks, and Terraform validation.
- Terraform provisions AWS ECS Fargate, RDS PostgreSQL, ALB, CloudWatch logs, security groups, and autoscaling-ready service primitives.

## Security and Compliance Notes

- No PAN or sensitive customer data is stored in the sample implementation.
- Transaction references are unique and idempotency-friendly.
- Audit logs are append-only at the application layer.
- Production deployments should add TLS, WAF, private subnets, Secrets Manager, KMS encryption, IAM least privilege, immutable log retention, database backups, and formal retention policies aligned with PCI DSS, SOC 2, FFIEC, and local regulatory obligations.
