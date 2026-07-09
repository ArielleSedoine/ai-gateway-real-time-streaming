# ☁️ AI Gateway Deployment Documentation

## 1. Overview

This document describes how to deploy the **AI Gateway – Real-Time Audio Streaming** service using Docker and Google Cloud Run.

The deployment workflow follows a cloud-native approach:

```
Developer

    |
    |
    ▼

Source Code Repository

    |
    |
    ▼

Docker Container Build

    |
    |
    ▼

Artifact Registry

    |
    |
    ▼

Google Cloud Run

    |
    |
    ▼

AI Gateway Service
```

The deployment architecture provides:

- Containerized execution
- Automated scaling
- Managed infrastructure
- Secure HTTPS endpoints
- Continuous delivery capability

---

# 2. Deployment Requirements

Before deploying the AI Gateway, ensure the following tools are installed.

## Required Tools

| Tool | Purpose |
|------|---------|
| Git | Source code management |
| Docker | Container creation |
| Google Cloud SDK | Cloud deployment |
| Python 3.11 | Local development |

---

## Google Cloud Requirements

A Google Cloud project is required with the following APIs enabled:

```
Cloud Run API
Artifact Registry API
Cloud Build API
IAM API
```

Enable APIs:

```bash
gcloud services enable \
run.googleapis.com \
artifactregistry.googleapis.com \
cloudbuild.googleapis.com \
iam.googleapis.com
```

---

# 3. Project Configuration

## Select Google Cloud Project

Authenticate:

```bash
gcloud auth login
```

Select the target project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Verify configuration:

```bash
gcloud config list
```

---

# 4. Containerization

The AI Gateway is deployed as a Docker container.

The container includes:

- Python runtime
- Application dependencies
- FastAPI service
- WebSocket server
- Audio processing libraries

---

## Dockerfile Example

Example container definition:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8080

CMD ["python", "src/main.py"]
```

---

# 5. Build Docker Image Locally

Build the container:

```bash
docker build \
-t ai-gateway .
```

Verify the image:

```bash
docker images
```

---

# 6. Run Container Locally

Start the service:

```bash
docker run \
-p 8080:8080 \
ai-gateway
```

Test the service:

```
http://localhost:8080
```

---

# 7. Artifact Registry Setup

Artifact Registry stores Docker images before deployment.

Create a repository:

```bash
gcloud artifacts repositories create ai-gateway-repo \
--repository-format=docker \
--location=us-east4 \
--description="AI Gateway Docker repository"
```

Configure Docker authentication:

```bash
gcloud auth configure-docker us-east4-docker.pkg.dev
```

---

# 8. Build and Push Container Image

Define variables:

```bash
PROJECT_ID=YOUR_PROJECT_ID

REGION=us-east4

IMAGE_NAME=ai-gateway
```

Build image:

```bash
docker build \
-t ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-gateway-repo/${IMAGE_NAME}:latest .
```

Push image:

```bash
docker push \
${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-gateway-repo/${IMAGE_NAME}:latest
```

---

# 9. Deploy to Google Cloud Run

Deploy the container:

```bash
gcloud run deploy ai-gateway \
--image ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-gateway-repo/${IMAGE_NAME}:latest \
--platform managed \
--region ${REGION}
```

---

# 10. Cloud Run Configuration

Recommended settings for real-time audio streaming:

## CPU

```
Minimum: 1 CPU
Recommended: 2 CPUs
```

---

## Memory

```
Minimum: 512Mi
Recommended: 1Gi+
```

---

## Concurrency

Cloud Run concurrency controls how many requests an instance handles.

For WebSocket streaming:

Recommended:

```
Concurrency: 10-50 sessions per instance
```

This depends on:

- Audio processing cost
- Instance resources
- Expected traffic

---

## Timeout

Long-lived WebSocket connections require an increased timeout.

Recommended:

```
Timeout:
3600 seconds
```

---

# 11. Environment Variables

Production configuration should use environment variables.

Example:

```env
ENVIRONMENT=production

HOST=0.0.0.0

PORT=8080

LOG_LEVEL=INFO

AI_SERVICE_URL=https://external-ai-service.example.com
```

For production secrets:

Use:

- Google Secret Manager
- Cloud Run environment configuration

---

# 12. WebSocket Configuration

Cloud Run supports WebSocket connections automatically.

Client connection:

```
wss://YOUR_CLOUD_RUN_URL/ws
```

Example flow:

```
Client

   |
   |
 WebSocket

   |
   ▼

Cloud Run

   |
   |
AI Gateway

```

---

# 13. Deployment Verification

After deployment:

Get service URL:

```bash
gcloud run services describe ai-gateway \
--region ${REGION} \
--format="value(status.url)"
```

Check logs:

```bash
gcloud run services logs read ai-gateway \
--region ${REGION}
```

Verify service status:

```bash
gcloud run services list
```

---

# 14. Continuous Deployment (Future)

Future CI/CD pipeline:

```
Developer

    |
    |
    ▼

GitHub Repository

    |
    |
    ▼

GitHub Actions

    |
    |
    ▼

Docker Build

    |
    |
    ▼

Artifact Registry

    |
    |
    ▼

Cloud Run Deployment
```

Possible automation:

- Automated tests
- Docker image build
- Security scanning
- Deployment approval
- Production rollout

---

# 15. Monitoring and Observability

Production monitoring should include:

## Application Metrics

- Active WebSocket connections
- Audio processing latency
- Translation response time
- Error rate


## Cloud Monitoring

Monitor:

- CPU usage
- Memory usage
- Instance count
- Request latency


## Logging

Recommended logs:

```
INFO:
Client connected

INFO:
Audio frame received

INFO:
Translation request sent

INFO:
Stream completed

ERROR:
Connection failure
```

---

# 16. Scaling Strategy

Cloud Run automatically scales based on demand.

Example:

```
Low Traffic

       |
       ▼

1 Instance


High Traffic

       |
       ▼

Multiple Instances
```

Future improvements:

- Session management service
- Distributed cache
- Regional deployment
- Kubernetes migration

---

# 17. Production Checklist

Before production release:

## Application

- [ ] Environment variables configured
- [ ] Logging enabled
- [ ] Error handling implemented
- [ ] Health checks available

## Container

- [ ] Docker image optimized
- [ ] Security scan completed
- [ ] Image stored in Artifact Registry

## Cloud Run

- [ ] Correct region selected
- [ ] Memory configured
- [ ] Timeout configured
- [ ] Scaling settings reviewed

## Security

- [ ] Authentication enabled
- [ ] Secrets secured
- [ ] IAM permissions reviewed

---

# Conclusion

The AI Gateway deployment architecture provides a scalable and production-ready approach for running real-time AI audio streaming workloads.

By combining Docker, Artifact Registry, Cloud Build, and Google Cloud Run, the system achieves:

- Reliable deployments
- Automatic scaling
- Simplified operations
- Cloud-native flexibility
- Low-latency AI communication
