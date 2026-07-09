# 🛠️ AI Gateway Troubleshooting Guide

## 1. Overview

This document provides solutions for common issues encountered while developing, running, deploying, and operating the **AI Gateway – Real-Time Audio Streaming** service.

The troubleshooting process covers:

- Local development issues
- Docker problems
- WebSocket connectivity
- Audio streaming issues
- Cloud Run deployment problems
- Performance and latency issues
- External AI service communication

---

# 2. General Debugging Workflow

When an issue occurs, follow this troubleshooting sequence:

```
Application Issue

      |
      ▼

Check Application Logs

      |
      ▼

Verify Configuration

      |
      ▼

Test Local Environment

      |
      ▼

Check Cloud Deployment

      |
      ▼

Analyze Performance Metrics
```

---

# 3. Application Startup Issues

## Problem

The application does not start locally.

Example:

```
Application failed to start
```

---

## Possible Causes

- Missing dependencies
- Incorrect Python version
- Invalid environment variables
- Port already in use
- Configuration errors

---

## Solutions

### Verify Python Version

```bash
python --version
```

Expected:

```
Python 3.11+
```

---

### Reinstall Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

### Check Environment Variables

Verify:

```env
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

---

### Check Running Ports

Linux/macOS:

```bash
lsof -i :8080
```

Windows:

```powershell
netstat -ano | findstr :8080
```

---

# 4. Docker Issues

# 4.1 Docker Build Failure

## Problem

Docker image creation fails.

Example:

```
ERROR: failed to build image
```

---

## Solutions

### Verify Docker Installation

```bash
docker --version
```

---

### Rebuild Without Cache

```bash
docker build --no-cache -t ai-gateway .
```

---

### Check Dockerfile

Verify:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
```

---

# 4.2 Container Does Not Start

## Problem

Container exits immediately.

Check logs:

```bash
docker logs <container_id>
```

---

Common causes:

- Application crash
- Missing dependencies
- Wrong startup command
- Invalid configuration

---

# 5. WebSocket Connection Issues

## Problem

Client cannot connect to the gateway.

Example:

```
WebSocket connection failed
```

---

## Check Endpoint

Local:

```
ws://localhost:8080/ws/audio
```

Production:

```
wss://YOUR_CLOUD_RUN_URL/ws/audio
```

---

## Common Causes

### Incorrect Protocol

HTTP:

```
http://
```

must become:

```
ws://
```

HTTPS:

```
https://
```

must become:

```
wss://
```

---

### Cloud Run HTTPS Requirement

Cloud Run requires secure WebSocket connections.

Production clients should use:

```
wss://
```

---

### Check Application Logs

Local:

```bash
python src/main.py
```

Cloud Run:

```bash
gcloud run services logs read ai-gateway
```

---

# 6. Audio Streaming Issues

## Problem

Audio is received but not processed correctly.

Symptoms:

- No translated audio
- Distorted sound
- High latency
- Broken stream

---

## Verify Audio Format

Supported example:

```
Codec:
Opus

Processing:
Opus → PCM → AI Service → PCM → Opus
```

---

## Common Causes

### Wrong Sample Rate

Verify audio configuration.

Recommended:

```
48000 Hz
```

---

### Incorrect Codec

Check:

```
Client codec
        |
        ▼
Gateway codec
        |
        ▼
AI service codec
```

All components must agree on the format.

---

### Audio Frame Size

Very large frames increase latency.

Recommended:

- Small streaming frames
- Continuous transmission
- No batching of full recordings

---

# 7. High Latency Problems

## Problem

Audio translation delay is too high.

---

## Possible Causes

- Large audio buffers
- Slow AI response
- Blocking operations
- Too many conversions
- Network latency

---

## Solutions

### Use Async Processing

Avoid:

```python
time.sleep()
```

Prefer:

```python
await asyncio.sleep()
```

---

### Reduce Buffer Size

Process:

```
Audio Frame

instead of:

Complete Audio File
```

---

### Monitor Latency

Measure:

```
Capture Time

      ↓

Gateway Receive Time

      ↓

AI Processing Time

      ↓

Client Playback Time
```

---

# 8. External AI Service Problems

## Problem

Gateway cannot communicate with AI service.

Example:

```
AI service connection failed
```

---

## Verify URL

Check:

```env
AI_SERVICE_URL=
```

---

## Test Connectivity

Example:

```bash
curl https://AI_SERVICE_ENDPOINT
```

---

## Common Causes

- Invalid endpoint
- Authentication failure
- Service unavailable
- Network restrictions

---

# 9. Cloud Run Deployment Issues

# 9.1 Deployment Failed

## Problem

Cloud Run deployment returns an error.

---

## Check Authentication

```bash
gcloud auth login
```

---

## Check Project

```bash
gcloud config get-value project
```

---

## Verify APIs

```bash
gcloud services list
```

Required:

```
Cloud Run API
Artifact Registry API
Cloud Build API
```

---

# 9.2 Container Failed to Start on Cloud Run

## Error Example

```
Container failed to start and listen on PORT
```

---

## Solution

Cloud Run requires the application to listen on:

```
PORT=8080
```

Example:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=int(os.getenv("PORT",8080))
)
```

---

# 10. Cloud Run Logs

View logs:

```bash
gcloud run services logs read ai-gateway \
--region us-east4
```

Filter errors:

```bash
gcloud logging read \
'severity>=ERROR'
```

---

# 11. Performance Debugging

Monitor:

## CPU

High CPU may indicate:

- Audio processing bottleneck
- Too many concurrent sessions


## Memory

High memory may indicate:

- Audio buffers not released
- Memory leaks


## Connections

Monitor:

- Active WebSockets
- Session duration
- Disconnect rate

---

# 12. Common Error Messages

| Error | Possible Cause | Solution |
|-|-|-|
| Connection refused | Service not running | Start application |
| Invalid codec | Unsupported audio format | Verify codec |
| Timeout | Slow processing | Reduce latency |
| 403 Forbidden | Authentication issue | Check permissions |
| 404 Not Found | Wrong endpoint | Verify URL |
| Container failed | Startup error | Check logs |
| Port error | Wrong Cloud Run port | Use PORT variable |

---

# 13. Development Checklist

Before reporting an issue:

- [ ] Application starts locally
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Docker image builds successfully
- [ ] WebSocket endpoint tested
- [ ] Logs collected
- [ ] Cloud Run status verified

---

# 14. Production Support Checklist

For production incidents:

1. Check Cloud Run status
2. Review application logs
3. Verify external AI service availability
4. Check latency metrics
5. Check resource utilization
6. Roll back deployment if required

---

# 15. Future Improvements

Future troubleshooting capabilities:

- Automated health checks
- Distributed tracing
- Centralized logging
- Error monitoring
- Performance dashboards
- Alerting system

---

# Conclusion

This troubleshooting guide provides a structured approach for diagnosing issues across the entire AI Gateway stack.

By following these steps, developers can quickly identify problems related to:

- Application execution
- Audio processing
- WebSocket communication
- Docker containers
- Cloud Run deployment
- External AI integrations
