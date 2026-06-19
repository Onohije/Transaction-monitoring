# Operations Runbook

## Failed Transaction Alert

Trigger: failed transaction count is greater than or equal to `FAILED_TX_THRESHOLD` inside `FAILED_TX_WINDOW_SECONDS`.

First response:

1. Check `/alerts` for observed count and timestamp.
2. Filter `/transactions?status=FAILED`.
3. Review `/logs` for related status changes and simulation or upstream events.
4. Group failures by reason code.
5. Escalate `HOST_TIMEOUT` and `REVERSAL_REQUIRED` to payment switch or core banking integration support.

## Production Monitoring

Recommended AWS setup:

- CloudWatch alarms for API 5xx, ALB target health, ECS CPU and memory, RDS CPU, RDS storage, RDS connection count, and database replication lag if read replicas are introduced.
- Prometheus metrics for transaction counts, failed counts, request latency, and worker saturation.
- Centralized immutable logs with retention controls.
- Pager routing for sustained failure-rate breaches.

## Data Protection

- Store secrets in AWS Secrets Manager.
- Encrypt RDS with KMS.
- Keep database in private subnets.
- Use IAM task roles with least privilege.
- Avoid storing PAN, CVV, PIN, or unnecessary PII.
- Add field-level tokenization where customer identifiers are required.

