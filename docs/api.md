# 📡 AI Gateway API Documentation

## 1. Overview

The AI Gateway exposes a real-time communication interface designed for low-latency multilingual audio streaming.

The API provides:

- Health monitoring endpoints
- WebSocket-based audio streaming
- Real-time bidirectional communication
- Audio frame exchange
- Session management

The primary communication channel is based on **WebSockets** because real-time audio processing requires:

- Low latency
- Persistent connections
- Full-duplex communication
- Continuous streaming

---

# 2. API Architecture

The communication flow is:

```
Client Application

        |
        |
        | WebSocket Connection
        |
        ▼

AI Gateway

        |
        |
        | Streaming Protocol
        |
        ▼

External AI Service
```

---

# 3. Base URL

## Local Development

```
http://localhost:8080
```

WebSocket endpoint:

```
ws://localhost:8080/ws/audio
```

---

## Production (Cloud Run)

Example:

```
https://ai-gateway-xxxxx-uc.a.run.app
```

WebSocket:

```
wss://ai-gateway-xxxxx-uc.a.run.app/ws/audio
```

---

# 4. REST API Endpoints

## 4.1 Health Check

### Endpoint

```
GET /health
```

### Purpose

Checks whether the AI Gateway service is running.

---

### Request

```http
GET /health HTTP/1.1
Host: localhost:8080
```

---

### Response

```json
{
  "status": "healthy",
  "service": "ai-gateway",
  "version": "1.0.0"
}
```

---

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Service available |
| 503 | Service unavailable |

---

# 5. WebSocket API

## 5.1 Audio Streaming Endpoint

### Endpoint

```
/ws/audio
```

Protocol:

```
WebSocket
```

Example:

```
ws://localhost:8080/ws/audio
```

---

# 6. Connection Lifecycle

The communication lifecycle follows these steps:

```
Client

  |
  |
  | Connect WebSocket
  |
  ▼

AI Gateway

  |
  |
  | Initialize Session
  |
  ▼

Audio Streaming

  |
  |
  | Process Frames
  |
  ▼

Translated Audio Stream

  |
  |
  ▼

Connection Closed
```

---

# 7. WebSocket Messages

The gateway exchanges two types of messages:

- Control messages
- Audio messages

---

# 7.1 Session Initialization

After connection, the client sends a session configuration message.

Example:

```json
{
  "type": "session_start",
  "session_id": "session-12345",
  "source_language": "en",
  "target_language": "fr",
  "audio_format": "opus"
}
```

---

## Parameters

| Field | Type | Description |
|-|-|-|
| type | string | Message type |
| session_id | string | Unique session identifier |
| source_language | string | Input language |
| target_language | string | Output language |
| audio_format | string | Audio codec |

---

# 7.2 Audio Frame Message

Audio data is streamed continuously.

Example:

```json
{
  "type": "audio",
  "timestamp": 1730000000,
  "codec": "opus",
  "data": "<binary_audio_frame>"
}
```

---

## Audio Parameters

| Field | Description |
|-|-|
| codec | Audio encoding format |
| timestamp | Frame timestamp |
| data | Encoded audio payload |

---

# 7.3 Translation Response

The gateway sends translated audio back.

Example:

```json
{
  "type": "audio_response",
  "codec": "opus",
  "language": "fr",
  "data": "<translated_audio_frame>"
}
```

---

# 8. Complete Streaming Example

## Client → Gateway

```
Audio Input

    |
    |
    ▼

Opus Frame

    |
    |
    ▼

WebSocket

    |
    |
    ▼

AI Gateway
```

---

## Gateway Processing

```
Receive Frame

       |
       ▼

Decode Opus

       |
       ▼

Convert PCM

       |
       ▼

Send to AI Service

       |
       ▼

Receive Translation

       |
       ▼

Encode Opus
```

---

## Gateway → Client

```
Translated Audio

        |
        |
        ▼

WebSocket Stream

        |
        |
        ▼

Client Playback
```

---

# 9. Error Handling

The API uses standard error messages.

Example:

```json
{
  "type": "error",
  "code": "INVALID_AUDIO_FORMAT",
  "message": "Unsupported audio codec"
}
```

---

## Error Codes

| Code | Description |
|-|-|
| INVALID_SESSION | Invalid session configuration |
| INVALID_AUDIO_FORMAT | Unsupported codec |
| CONNECTION_ERROR | WebSocket failure |
| AI_SERVICE_ERROR | External AI service failure |
| INTERNAL_ERROR | Gateway processing error |

---

# 10. Authentication (Future)

Future versions may support:

- JWT authentication
- API keys
- OAuth2
- Google Cloud IAM integration

Example:

```http
Authorization: Bearer <token>
```

---

# 11. Rate Limiting (Future)

Production deployments should implement:

- Maximum concurrent sessions
- Maximum audio duration
- Client quotas
- Abuse prevention

---

# 12. Performance Considerations

The API is optimized for real-time workloads.

Important parameters:

| Parameter | Goal |
|-|-|
| Latency | Minimize end-to-end delay |
| Connection | Persistent WebSocket |
| Processing | Async streaming |
| Audio | Small frame processing |
| Scaling | Cloud Run autoscaling |

---

# 13. Client Integration Example

Python example:

```python
import asyncio
import websockets


async def stream_audio():

    uri = "ws://localhost:8080/ws/audio"

    async with websockets.connect(uri) as websocket:

        await websocket.send(
            {
                "type": "session_start",
                "source_language": "en",
                "target_language": "fr"
            }
        )

        while True:
            audio_frame = capture_audio()

            await websocket.send(audio_frame)

            response = await websocket.recv()

            play_audio(response)


asyncio.run(stream_audio())
```

---

# 14. API Versioning Strategy

Future versions should support:

```
/api/v1/ws/audio
```

Example:

```
ws://localhost:8080/api/v1/ws/audio
```

Benefits:

- Backward compatibility
- Controlled API evolution
- Multiple client versions

---

# 15. Summary

The AI Gateway API provides a real-time communication interface optimized for AI-powered audio applications.

Key characteristics:

- WebSocket-based streaming
- Full-duplex communication
- Low-latency audio processing
- Extensible AI service integration
- Cloud-native deployment compatibility

The API is designed to support future extensions such as authentication, monitoring, multi-language processing, and large-scale deployments.
