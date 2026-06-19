# Bank Transaction Monitoring Architecture

## Goals

The platform gives banking operations, reconciliation, and incident teams a near-real-time view of transaction health. It focuses on transparent status tracking, configurable failed-transaction alerting, auditability, and deployability through repeatable DevOps workflows.

## Functional Design

### Transaction Workflow

1. `RECEIVED`: transaction enters the monitoring boundary.
2. `VALIDATED`: basic structural, account, channel, amount, and duplicate-reference checks pass.
3. `POSTED`: transaction is accepted by the posting/core banking layer.
4. `SETTLED`: transaction reaches final successful state.
5. `FAILED`: transaction cannot complete and requires investigation or automated retry/reversal.
6. `REVERSED`: compensating entry completed after a failed or disputed transaction.

Each state change is written to `transaction_history` and mirrored to `audit_logs`.

### Alerting

The first implemented alert is failed-transaction threshold detection:

- Threshold: `FAILED_TX_THRESHOLD`
- Window: `FAILED_TX_WINDOW_SECONDS`
- Signal: count of transactions in `FAILED` status created inside the rolling window

Production extensions should include channel-specific thresholds, reason-code thresholds, core-host timeout rates, settlement aging, duplicate-reference spikes, and reversal SLA breaches.

## Data Model

- `transactions`: current transaction state, reference, account identifier, channel, amount, currency, reason code, timestamps.
- `transaction_history`: append-style status history.
- `alerts`: generated operational alerts.
- `audit_logs`: system events and status changes for troubleshooting and audit review.

PostgreSQL is used because transaction monitoring requires strong consistency, indexed querying, reliable commits, backup/restore support, and mature operational tooling.

## AWS Production Topology

Recommended production deployment:

- Amazon ECS Fargate for API and web workloads.
- Amazon RDS for PostgreSQL in private subnets with encryption, backups, and multi-AZ enabled.
- Application Load Balancer with TLS certificates from ACM.
- AWS WAF on public entry points.
- Secrets Manager for database credentials and service secrets.
- CloudWatch Logs for container logs.
- CloudWatch alarms plus Prometheus/Grafana for metrics and operational dashboards.
- ECR for versioned container images.
- VPC with public subnets for ALB and private subnets for ECS tasks and RDS.

## Security Controls

- Do not store PAN, CVV, PIN, or unnecessary PII.
- Tokenize customer/account identifiers where operationally feasible.
- Use TLS in transit and KMS encryption at rest.
- Apply IAM least privilege to ECS task roles.
- Keep RDS inaccessible from the public internet.
- Retain audit logs according to regulatory and internal policy.
- Add SSO/RBAC before production use.
- Add rate limiting and request correlation IDs at the API edge.

## CI/CD

The included GitHub Actions workflow validates API tests, frontend build, container builds, and Terraform configuration. A mature release path should add:

- SBOM generation.
- Dependency and image scanning.
- SAST checks.
- Signed images.
- Promotion gates by environment.
- Blue/green or canary deployment strategy.
- Database migration checks before release.

## Monitoring and Maintenance

Operational signals to track:

- API latency, error rate, and saturation.
- Transaction volume by status and channel.
- Failure rate by reason code.
- Alert frequency and acknowledgement time.
- PostgreSQL CPU, memory, locks, connections, slow queries, and storage.
- ECS task restarts, CPU, memory, and deployment health.

Incident response should start from the alert, drill into failed transactions, correlate with audit logs, group by reason code/channel, and escalate to core banking, switch, network, or database support depending on failure pattern.

