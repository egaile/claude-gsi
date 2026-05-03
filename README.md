# GSI Reference Architecture Generator

> A partner enablement tool that helps Global System Integrators rapidly generate healthcare-specific enterprise AI deployment architectures.

[![Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://gsi-arch-generator.vercel.app)
[![AI Agnostic](https://img.shields.io/badge/AI-provider%20agnostic-2563eb)](#)

## The Problem

GSI partners face a consistent bottleneck when deploying AI for enterprise healthcare customers:

- **Architecture Design Time**: Each engagement requires custom architecture work, even when patterns are similar across customers
- **Compliance Complexity**: HIPAA, PHI handling, and BAA requirements must be addressed in every deployment
- **Provider Choice**: Customers may standardize on Claude, OpenAI ChatGPT, or another approved LLM provider
- **Cloud Platform Variance**: Customers deploy on AWS or Google Cloud, each with different integration patterns
- **Knowledge Transfer**: Senior architects become bottlenecks because institutional knowledge is not codified

## The Solution

This tool generates 80% of a reference architecture in seconds, including industry-specific compliance considerations, AI-provider guidance, cloud deployment patterns, and security best practices.

The product is intentionally AI agnostic: users select a deployment cloud and select the LLM provider independently.

## Features

### Healthcare-Focused Use Cases
- Clinical Documentation Assistance
- Prior Authorization Automation
- Medical Coding Support
- Patient Communication

### AI Provider Selection
- Claude
- OpenAI ChatGPT

### Multi-Cloud Support
- AWS healthcare AI deployment patterns
- Google Cloud healthcare AI deployment patterns

### Generated Outputs
- **Executive Summary**: Customer-ready business value, implementation focus, and next steps
- **Architecture Diagram**: Interactive Mermaid visualization with PHI touchpoints highlighted
- **HIPAA Compliance Checklist**: Administrative, physical, and technical safeguards
- **Deployment Guide**: Step-by-step infrastructure setup, IAM policies, network config
- **Implementation Roadmap**: Phased delivery plan from discovery through scale
- **Risk Register**: Enterprise implementation risks with mitigation and ownership
- **Sample Code**: Python and TypeScript integration examples tailored to the selected AI provider

## Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌────────────────────┐
│                 │     │                 │     │                    │
│  React + Vite   │────▶│  FastAPI        │────▶│  Selected AI       │
│  TailwindCSS    │     │  Python 3.11    │     │  Provider API      │
│                 │     │                 │     │                    │
└─────────────────┘     └─────────────────┘     └────────────────────┘
     Frontend               Backend              AI Generation
     (Vercel)            (Railway/Render)
```

### Key Technical Decisions

- **Provider-Agnostic Generation**: The backend routes generation to Claude or OpenAI ChatGPT based on the request
- **Parallel Section Streaming**: Architecture, compliance, and deployment sections generate independently and stream as they complete
- **In-Memory Response Cache**: Repeated demo configurations return quickly from a process-local cache
- **Mermaid.js for Diagrams**: Code-based diagrams that render consistently and export cleanly
- **FastAPI Backend**: Clean async handling for AI provider API calls with proper error handling
- **TypeScript Frontend**: Strong typing prevents runtime errors and improves maintainability

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- At least one AI provider API key: Anthropic or OpenAI

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Environment Variables

**Frontend** (`.env`)
```env
VITE_API_URL=http://localhost:8000
```

**Backend** (`.env`)
```env
# Configure one or both providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional model overrides
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-5.2

CORS_ORIGINS=http://localhost:5173
```

## Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── lib/            # API client, types, utilities
│   │   └── App.tsx         # Main application
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── services/       # AI provider integration
│   │   └── models.py       # Request/response models
│   ├── prompts/            # Provider-neutral prompt context
│   └── requirements.txt
├── docs/
│   ├── PRD.md
│   ├── API.md
│   └── ARCHITECTURE.md
├── CLAUDE.md               # Development context
├── AGENTS.md               # Codex development context
└── README.md
```

## Healthcare Domain Expertise

This tool embeds healthcare IT knowledge across:

- HIPAA administrative, physical, and technical safeguards
- BAA requirements for cloud services and AI providers
- Minimum necessary principle for PHI access
- EHR systems via FHIR APIs
- Payer systems via X12 EDI transactions
- Clinical coding systems such as ICD-10 and CPT
- AWS HealthLake and Comprehend Medical
- Google Cloud Healthcare API and healthcare AI services

## About

Built by [Ed Gaile](https://linkedin.com/in/edgaile) as a portfolio project demonstrating enterprise AI partner enablement: technical depth, strategic thinking, and practical GSI delivery value.
