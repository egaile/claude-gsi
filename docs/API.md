# API Reference

## Reference Architecture Generator API

Base URL: `http://localhost:8000` (development) or your deployed backend URL.

---

## Authentication

The API does not require authentication for requests. However, the backend requires an `ANTHROPIC_API_KEY` environment variable to communicate with Claude.

---

## Endpoints

### Health Check

Check if the API is running and properly configured.

```
GET /api/health
```

**Response**

```json
{
  "status": "healthy",
  "service": "gsi-architecture-generator"
}
```

**Status Codes**

| Code | Description |
|------|-------------|
| 200 | Service is healthy |
| 503 | Service not initialized (missing API key) |

---

### Generate Architecture

Generate a healthcare reference architecture based on the provided configuration.

```
POST /api/generate-architecture
```

**Request Headers**

| Header | Value |
|--------|-------|
| Content-Type | application/json |

**Request Body**

```json
{
  "useCase": "clinical-documentation",
  "cloudPlatform": "aws-bedrock",
  "integrationPattern": "api-gateway",
  "dataClassification": "phi",
  "scaleTier": "production"
}
```

**Request Fields**

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `useCase` | string | Yes | `clinical-documentation`, `prior-authorization`, `medical-coding`, `patient-communication` |
| `cloudPlatform` | string | Yes | `aws-bedrock`, `gcp-vertex` |
| `integrationPattern` | string | Yes | `api-gateway`, `event-driven`, `batch-processing` |
| `dataClassification` | string | Yes | `phi`, `pii`, `de-identified`, `public` |
| `scaleTier` | string | Yes | `pilot`, `production`, `enterprise` |

**Response**

```json
{
  "architecture": {
    "mermaidDiagram": "flowchart TD\n    ...",
    "components": [
      {
        "name": "API Gateway",
        "service": "Amazon API Gateway",
        "purpose": "Entry point for all API requests with authentication",
        "phiTouchpoint": false
      }
    ],
    "dataFlows": [
      {
        "from": "EHR System",
        "to": "API Gateway",
        "data": "Clinical documentation request",
        "encrypted": true
      }
    ]
  },
  "compliance": {
    "checklist": [
      {
        "category": "technical",
        "requirement": "Encryption at rest",
        "implementation": "Enable AWS KMS encryption for all data stores",
        "priority": "required"
      }
    ],
    "baaRequirements": "Obtain BAA from Anthropic for Claude API usage..."
  },
  "deployment": {
    "steps": [
      "Create VPC with private subnets",
      "Deploy API Gateway with WAF",
      "..."
    ],
    "iamPolicies": [
      "{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [...]\n}"
    ],
    "networkConfig": "VPC CIDR: 10.0.0.0/16\nPrivate Subnets: 10.0.1.0/24, 10.0.2.0/24\n...",
    "monitoringSetup": "CloudWatch Logs for all Lambda functions..."
  },
  "sampleCode": {
    "python": "import anthropic\n\nclient = anthropic.Anthropic()\n...",
    "typescript": "import Anthropic from '@anthropic-ai/sdk';\n..."
  }
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `architecture.mermaidDiagram` | string | Mermaid flowchart syntax for the architecture diagram |
| `architecture.components` | array | List of infrastructure components |
| `architecture.components[].name` | string | Component display name |
| `architecture.components[].service` | string | Cloud service name |
| `architecture.components[].purpose` | string | What the component does |
| `architecture.components[].phiTouchpoint` | boolean | Whether component handles PHI |
| `architecture.dataFlows` | array | Data movement between components |
| `architecture.dataFlows[].from` | string | Source component |
| `architecture.dataFlows[].to` | string | Destination component |
| `architecture.dataFlows[].data` | string | What data is transferred |
| `architecture.dataFlows[].encrypted` | boolean | Whether transfer is encrypted |
| `compliance.checklist` | array | HIPAA compliance requirements |
| `compliance.checklist[].category` | string | `administrative`, `physical`, or `technical` |
| `compliance.checklist[].requirement` | string | The compliance requirement |
| `compliance.checklist[].implementation` | string | How to implement it |
| `compliance.checklist[].priority` | string | `required`, `recommended`, or `addressable` |
| `compliance.baaRequirements` | string | Business Associate Agreement guidance |
| `deployment.steps` | array | Ordered deployment instructions |
| `deployment.iamPolicies` | array | IAM policy JSON strings |
| `deployment.networkConfig` | string | Network configuration details |
| `deployment.monitoringSetup` | string | Monitoring and logging setup |
| `sampleCode.python` | string | Python integration example |
| `sampleCode.typescript` | string | TypeScript integration example |

**Status Codes**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid request (validation error) |
| 500 | Server error (Claude API failure, parsing error) |
| 503 | Service not initialized |

---

### Generate Architecture (Streaming)

Stream architecture generation with Server-Sent Events (SSE). Returns sections progressively as they complete. Does NOT include sample code (use the separate code generation endpoint).

```
POST /api/generate-architecture-stream
```

**Request Headers**

| Header | Value |
|--------|-------|
| Content-Type | application/json |

**Request Body**

Same as `/api/generate-architecture`.

**Response**

The response is a stream of Server-Sent Events:

```
event: section
data: {"section": "architecture", "data": {...}}

event: section
data: {"section": "compliance", "data": {...}}

event: section
data: {"section": "deployment", "data": {...}}

event: done
data: {"status": "complete"}
```

**Event Types**

| Event | Description |
|-------|-------------|
| `section` | A completed section (architecture, compliance, or deployment) |
| `done` | Stream complete |
| `error` | An error occurred |

**Status Codes**

| Code | Description |
|------|-------------|
| 200 | Streaming started successfully |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

### Generate Code

Generate sample code based on an architecture configuration. Call this after receiving the architecture to get Python and TypeScript integration examples.

```
POST /api/generate-code
```

**Request Headers**

| Header | Value |
|--------|-------|
| Content-Type | application/json |

**Request Body**

```json
{
  "useCase": "clinical-documentation",
  "cloudPlatform": "aws-bedrock",
  "architectureSummary": "Components: API Gateway (Amazon API Gateway), Claude Service (AWS Bedrock). PHI touchpoints: AWS Bedrock."
}
```

**Request Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `useCase` | string | Yes | Same values as generate-architecture |
| `cloudPlatform` | string | Yes | Same values as generate-architecture |
| `architectureSummary` | string | Yes | Brief description of the architecture components |

**Response**

```json
{
  "sampleCode": {
    "python": "import anthropic\n\nclient = anthropic.Anthropic()\n...",
    "typescript": "import Anthropic from '@anthropic-ai/sdk';\n..."
  }
}
```

**Status Codes**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid request |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Errors**

| Error | Cause | Solution |
|-------|-------|----------|
| `Service not initialized` | Missing ANTHROPIC_API_KEY | Set the environment variable |
| `Failed to parse Claude response as JSON` | Claude returned invalid JSON | Retry the request |
| `value is not a valid enumeration member` | Invalid enum value in request | Check allowed values |

---

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/api/generate-architecture \
  -H "Content-Type: application/json" \
  -d '{
    "useCase": "clinical-documentation",
    "cloudPlatform": "aws-bedrock",
    "integrationPattern": "api-gateway",
    "dataClassification": "phi",
    "scaleTier": "production"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate-architecture",
    json={
        "useCase": "clinical-documentation",
        "cloudPlatform": "aws-bedrock",
        "integrationPattern": "api-gateway",
        "dataClassification": "phi",
        "scaleTier": "production",
    },
)

if response.ok:
    data = response.json()
    print(data["architecture"]["mermaidDiagram"])
else:
    print(f"Error: {response.json()['detail']}")
```

### TypeScript/JavaScript

```typescript
const response = await fetch("http://localhost:8000/api/generate-architecture", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    useCase: "clinical-documentation",
    cloudPlatform: "aws-bedrock",
    integrationPattern: "api-gateway",
    dataClassification: "phi",
    scaleTier: "production",
  }),
});

if (response.ok) {
  const data = await response.json();
  console.log(data.architecture.mermaidDiagram);
} else {
  const error = await response.json();
  console.error(`Error: ${error.detail}`);
}
```

---

## OpenAPI/Swagger

FastAPI automatically generates OpenAPI documentation. When the backend is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Rate Limiting

The API implements in-memory rate limiting:

| Limit | Value |
|-------|-------|
| Requests per minute | 10 per IP |
| Reset | On serverless cold start |

**Rate Limit Response**

```json
{
  "detail": "Rate limit exceeded. Please wait before making another request."
}
```

**Status Code**: 429 Too Many Requests

For production, consider using persistent rate limiting with Redis or Vercel KV.

---

## Timeouts

| Operation | Timeout |
|-----------|---------|
| Claude API call | 120 seconds |
| Full generation | ~90 seconds |
| Streaming generation | ~45-50 seconds |
| Code generation | ~30-40 seconds |
| Frontend request | 180 seconds (streaming), 120 seconds (non-streaming) |

The streaming endpoint reduces perceived latency by showing content as it generates.
