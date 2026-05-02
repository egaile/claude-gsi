# Example Output Format

This file contains provider-neutral example output to guide AI models in generating properly structured architecture responses.

## Example: Clinical Documentation on AWS with Selected AI Provider

```json
{
  "architecture": {
    "mermaidDiagram": "flowchart TD\n    subgraph Client[\"Healthcare Application\"]\n        ehr[EHR System\\nEpic/Cerner]\n        app[Clinical App]\n    end\n\n    subgraph Cloud[\"Deployment Cloud - HIPAA Eligible Services\"]\n        apigw[API Gateway + WAF]\n        processor[Serverless Processor]\n        phi[PHI Detection / De-identification]\n        llm[Selected AI Provider]\n        fhir[(FHIR Store)]\n        archive[(Encrypted Document Archive)]\n        secrets[Secret Manager]\n        kms[KMS]\n        logs[Audit Logs]\n    end\n\n    ehr -->|FHIR R4| apigw\n    app -->|REST API| apigw\n    apigw -->|Authorized request| processor\n    processor -->|Detect or redact PHI| phi\n    processor -->|Prompt with approved data| llm\n    processor -->|Store reviewed note| fhir\n    processor -->|Archive source document| archive\n    processor -.->|Read provider credentials| secrets\n    archive -.->|Encrypt| kms\n    processor -.->|Audit events| logs\n\n    style llm fill:#2563eb,color:#fff\n    style phi fill:#10b981,color:#fff\n    style fhir fill:#f59e0b,color:#fff",
    "components": [
      {
        "name": "API Gateway",
        "service": "Cloud-native API gateway",
        "purpose": "Authenticates requests, enforces rate limits, and routes healthcare application traffic",
        "phiTouchpoint": false
      },
      {
        "name": "Document Processor",
        "service": "Serverless compute",
        "purpose": "Coordinates validation, PHI controls, model invocation, and persistence",
        "phiTouchpoint": true
      },
      {
        "name": "Selected AI Provider",
        "service": "Configured LLM provider endpoint",
        "purpose": "Generates AI-assisted clinical documentation output using the selected provider",
        "phiTouchpoint": true
      }
    ],
    "dataFlows": [
      {
        "from": "EHR System",
        "to": "API Gateway",
        "data": "FHIR clinical documentation request",
        "encrypted": true
      },
      {
        "from": "Document Processor",
        "to": "Selected AI Provider",
        "data": "Approved prompt payload with minimum necessary clinical context",
        "encrypted": true
      }
    ]
  },
  "compliance": {
    "checklist": [
      {
        "category": "technical",
        "requirement": "Encryption in transit and at rest",
        "implementation": "Use TLS 1.2+ for all data flows and customer-managed keys for stored PHI",
        "priority": "required"
      },
      {
        "category": "administrative",
        "requirement": "Business Associate Agreement",
        "implementation": "Execute BAAs with the deployment cloud and selected AI provider before processing PHI",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Audit logging",
        "implementation": "Log user, request ID, model invocation metadata, and access decisions without storing raw PHI in logs",
        "priority": "required"
      }
    ],
    "baaRequirements": "Execute and verify BAAs with every service that creates, receives, maintains, or transmits PHI, including the selected AI provider and deployment cloud services. Confirm the specific model, region, and data retention configuration are approved for healthcare workloads."
  },
  "deployment": {
    "steps": [
      "Confirm the selected AI provider, model, region, and BAA coverage for PHI workloads",
      "Create isolated network resources and private subnets for application processing",
      "Configure secret storage for AI provider credentials and rotate keys on a defined schedule",
      "Deploy the API gateway, processing service, PHI detection layer, encrypted storage, and audit logging",
      "Run validation tests for authentication, authorization, prompt redaction, and audit evidence"
    ],
    "iamPolicies": [
      "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"secretsmanager:GetSecretValue\"],\"Resource\":\"arn:example:secret:selected-ai-provider-key\"}]}"
    ],
    "networkConfig": "Use private subnets for compute, controlled outbound egress to the selected AI provider endpoint, TLS enforcement, and network logs for audit review.",
    "monitoringSetup": "Track request volume, model latency, token usage, error rates, denied access attempts, and PHI-control failures. Alert on abnormal usage and authentication failures."
  },
  "sampleCode": {
    "python": "# Provider-specific Python sample code is generated for the selected AI provider.",
    "typescript": "// Provider-specific TypeScript sample code is generated for the selected AI provider."
  }
}
```
