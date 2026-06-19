# Build and Run Guide

This project can be built and verified in three practical ways:

1. Local Docker workflow.
2. GitHub Actions workflow.
3. Azure DevOps workflow.

Use the Docker path first when learning the application. Use GitHub Actions or Azure DevOps when you want automated validation on every push or pull request.

## Step 1: Build and Run Locally with Docker

### 1. Open the project folder

In VS Code, open:

```text
C:\Users\HP\Documents\Codex\2026-06-19\bank-transaction-monitoring-dashboard\outputs\bank-transaction-monitoring-dashboard
```

### 2. Confirm Docker Desktop is running

Open Docker Desktop and wait until it says the engine is running.

Check from the VS Code terminal:

```bash
docker version
docker compose version
```

### 3. Start the full stack

From the project root, run:

```bash
docker compose up --build
```

This starts:

- PostgreSQL on `localhost:5432`
- API on `localhost:8000`
- Web dashboard on `localhost:8080`
- Prometheus on `localhost:9090`

### 4. Open the services

- Dashboard: `http://localhost:8080`
- API documentation: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`

### 5. Generate transactions

Use the dashboard `Simulate` button, or call the API:

```bash
curl -X POST http://localhost:8000/simulate ^
  -H "Content-Type: application/json" ^
  -d "{\"count\":40,\"failure_rate\":0.25}"
```

On PowerShell, you can also use:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/simulate `
  -ContentType "application/json" `
  -Body '{"count":40,"failure_rate":0.25}'
```

### 6. Check transaction monitoring outputs

```bash
curl http://localhost:8000/summary
curl http://localhost:8000/transactions
curl http://localhost:8000/alerts
curl http://localhost:8000/logs
```

### 7. Stop the stack

```bash
docker compose down
```

To remove the local database volume as well:

```bash
docker compose down -v
```

## Step 2: Validate with GitHub Actions

The GitHub Actions workflow is located at:

```text
.github/workflows/ci.yml
```

It performs four checks:

- Installs Python dependencies and runs API tests.
- Installs Node dependencies and builds the React dashboard.
- Builds Docker images with Docker Compose.
- Validates Terraform configuration.

### 1. Push the project to GitHub

From the project root:

```bash
git init
git add .
git commit -m "Initial bank transaction monitoring dashboard"
git branch -M main
git remote add origin https://github.com/<your-org>/<your-repo>.git
git push -u origin main
```

Replace `<your-org>` and `<your-repo>` with your real GitHub organization/user and repository name.

### 2. Watch the pipeline

In GitHub:

1. Open the repository.
2. Go to `Actions`.
3. Select the `ci` workflow.
4. Confirm all jobs pass.

### 3. What success means

A passing workflow confirms:

- The API imports and tests run.
- The frontend compiles.
- Docker image definitions are buildable.
- Terraform syntax and provider configuration are valid enough for CI validation.

For production, extend the workflow with image publishing to Amazon ECR, vulnerability scanning, SBOM generation, signed images, and environment-based deployment approvals.

## Step 3: Validate with Azure DevOps

The Azure DevOps pipeline is located at:

```text
azure-pipelines.yml
```

It performs:

- API dependency install and tests.
- React dependency install and production build.
- Docker Compose configuration validation.
- Docker Compose image build.

### 1. Create an Azure DevOps project

In Azure DevOps:

1. Create or open an organization.
2. Create a project.
3. Go to `Repos`.
4. Import or push this repository.

### 2. Create the pipeline

In Azure DevOps:

1. Go to `Pipelines`.
2. Select `New pipeline`.
3. Choose your repository source.
4. Select `Existing Azure Pipelines YAML file`.
5. Choose:

```text
/azure-pipelines.yml
```

6. Save and run.

### 3. Read the pipeline stages

The pipeline has two stages:

```text
Validate
ContainerBuild
```

`Validate` proves the API and web application can build independently.

`ContainerBuild` proves the local container packaging is valid.

### 4. Recommended production extension

For a real banking delivery pipeline, add these Azure DevOps capabilities:

- Publish API and web Docker images to Azure Container Registry or Amazon ECR.
- Run dependency scanning and container image scanning.
- Store secrets in Azure Key Vault or AWS Secrets Manager.
- Use deployment environments with approvals.
- Deploy infrastructure through Terraform.
- Require pull request validation before merging to `main`.

## Troubleshooting

### Docker cannot connect

Error example:

```text
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

Fix: start Docker Desktop and wait until the engine is ready.

### Port already in use

If `8000`, `8080`, `9090`, or `5432` are already used, edit `docker-compose.yml` and change the published port on the left side.

Example:

```yaml
ports:
  - "8081:80"
```

### Frontend cannot reach API

Confirm the API is available:

```bash
curl http://localhost:8000/health
```

Then confirm the web build argument in `docker-compose.yml` points to:

```text
http://localhost:8000
```

### Alerts do not appear

Generate enough failed transactions to breach the threshold:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/simulate `
  -ContentType "application/json" `
  -Body '{"count":50,"failure_rate":0.8}'
```

Default alert settings:

- `FAILED_TX_THRESHOLD=5`
- `FAILED_TX_WINDOW_SECONDS=300`

