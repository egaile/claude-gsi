# Product Requirements Document

## Product

The GSI Reference Architecture Generator helps Global System Integrator partners create healthcare-specific enterprise AI reference architectures. It supports multiple LLM providers, currently Claude and OpenAI ChatGPT, without making either provider the center of the product experience.

## Problem

GSI teams repeatedly need to design secure, compliant AI architectures for healthcare customers. Each engagement requires healthcare workflow knowledge, HIPAA/PHI controls, deployment-cloud expertise, and provider-specific LLM integration details. Senior architects often become bottlenecks, and architecture quality can vary across teams.

## Goals

- Generate proposal-ready healthcare AI reference architectures in minutes.
- Let users choose deployment cloud and AI provider independently.
- Produce provider-specific implementation details while keeping product language AI agnostic.
- Codify HIPAA, PHI handling, BAA, audit, networking, and security best practices.
- Provide code examples that match the selected provider and cloud deployment pattern.

## Non-Goals

- Replace final review by healthcare, security, privacy, or legal teams.
- Guarantee that a specific provider/model/region is approved for PHI without customer contract validation.
- Deploy infrastructure automatically.
- Store generated PHI or customer data.

## Target Users

| User | Need |
|------|------|
| GSI Pre-Sales Engineer | Customer-ready architecture collateral |
| Partner Solution Architect | Repeatable patterns across regulated healthcare accounts |
| Healthcare Enterprise Architect | Initial deployment approach for AI use cases |
| Delivery Lead | Accelerated discovery and implementation planning |

## Scope

### Inputs

- Healthcare use case
- Deployment cloud: AWS or Google Cloud
- AI provider: Claude or OpenAI ChatGPT
- Integration pattern: API gateway, event-driven, or batch processing
- Data classification: PHI, PII, de-identified, or public
- Scale tier: pilot, production, or enterprise

### Outputs

- Mermaid architecture diagram
- Executive summary with business value, implementation focus, and recommended next steps
- Component inventory with PHI touchpoints
- Data flows with encryption indicators
- HIPAA compliance checklist
- BAA requirements for selected cloud services and AI provider
- Deployment guide with IAM, networking, and monitoring guidance
- Implementation roadmap with phases, activities, and exit criteria
- Risk register with impact, likelihood, mitigation, and owner
- Python and TypeScript sample code for the selected AI provider

## Functional Requirements

1. The user can select Claude or OpenAI ChatGPT as the AI provider.
2. The user can select AWS or Google Cloud as the deployment target.
3. The backend sends generation requests to the selected AI provider.
4. The generated architecture consistently names the selected provider in diagrams, compliance notes, and code.
5. The generated guidance remains provider-neutral where the provider does not matter.
6. The streaming endpoint progressively returns architecture, compliance, and deployment sections.
7. Sample code is generated on demand and includes provider-specific SDK/API usage.
8. The API returns a clear configuration error when the selected provider key is not configured.
9. The streaming endpoint generates major sections in parallel to improve first-result latency.
10. The backend caches generated section sets for repeated configurations.

## Technical Requirements

| Area | Requirement |
|------|-------------|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI + Pydantic |
| Provider SDKs | Anthropic SDK and OpenAI SDK |
| Streaming | Server-Sent Events |
| Validation | Zod on frontend, Pydantic on backend |
| Configuration | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, optional model env vars |

## Compliance Requirements

- BAA guidance must include the selected AI provider and deployment cloud.
- PHI touchpoints must be explicitly marked.
- Generated logging guidance must avoid raw PHI in logs.
- Generated code must include comments for PHI handling and audit controls.
- Human review should be included for clinical output workflows.

## Success Metrics

- Architecture generation completes successfully for all supported input combinations.
- Generated output validates against the response schema.
- Users can switch providers without changing deployment-cloud selections.
- Documentation and UI describe the product as an enterprise AI architecture tool, not as a single-vendor demo.
- Repeated demo configurations return from cache with minimal latency.
