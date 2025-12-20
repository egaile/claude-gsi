# GSI Reference Architecture Generator

> A partner enablement tool that helps Global System Integrators rapidly generate healthcare-specific Claude deployment architectures.

[![Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://gsi-arch-generator.vercel.app)
[![Built with Claude](https://img.shields.io/badge/built%20with-Claude-8B5CF6)](https://anthropic.com)

## The Problem

GSI partners face a consistent bottleneck when deploying Claude for enterprise healthcare customers:

- **Architecture Design Time**: Each engagement requires custom architecture work, even when patterns are similar across customers
- **Compliance Complexity**: HIPAA, PHI handling, and BAA requirements must be addressed in every deployment
- **Cloud Platform Variance**: Customers deploy on AWS Bedrock or GCP Vertex—each with different integration patterns
- **Knowledge Transfer**: Senior architects become bottlenecks because institutional knowledge isn't codified

## The Solution

This tool generates 80% of a reference architecture in seconds—including industry-specific compliance considerations, cloud platform deployment patterns, and security best practices.

**The meta insight**: This tool uses Claude to generate architectures, demonstrating the product while building tools that help partners sell it.

## Demo

![Architecture Generator Demo](docs/demo.gif)

**Try it**: [claude-gsi.vercel.app](https://claude-gsi.vercel.app/)

## Features

### 🏥 Healthcare-Focused Use Cases
- Clinical Documentation Assistance
- Prior Authorization Automation
- Medical Coding Support
- Patient Communication

### ☁️ Multi-Cloud Support
- AWS Bedrock deployment patterns
- GCP Vertex AI deployment patterns

### 📋 Generated Outputs
- **Architecture Diagram**: Interactive Mermaid visualization with PHI touchpoints highlighted
- **HIPAA Compliance Checklist**: Administrative, physical, and technical safeguards
- **Deployment Guide**: Step-by-step infrastructure setup, IAM policies, network config
- **Sample Code**: Python and TypeScript integration examples

## Partner Enablement Strategy

This tool represents a scalable approach to GSI enablement that moves beyond one-off architecture consulting:

### Current State
```
Anthropic PSA → Works with GSI → GSI delivers to Customer
                (bottleneck)     (slow ramp-up)
```

### Enabled State
```
Anthropic PSA → Builds enablement tools → GSI self-serves → Faster customer delivery
                (scales impact)           (no bottleneck)   (consistent quality)
```

### Why This Matters

1. **Accelerates Time-to-Deployment**: Partners can generate proposal-ready architectures in minutes instead of days
2. **Codifies Best Practices**: Institutional knowledge becomes accessible tooling
3. **Maintains Quality**: Generated architectures follow Anthropic-approved patterns
4. **Scales Partner Capacity**: Junior architects can deliver senior-quality work

### Expansion Path

| Phase | Scope | Value |
|-------|-------|-------|
| MVP | Healthcare + 2 clouds | Prove the concept |
| Phase 2 | Financial Services, Public Sector | Broader partner coverage |
| Phase 3 | ROI Calculator, Training Hub | Complete enablement suite |
| Phase 4 | Partner-contributed templates | Community-driven growth |

## Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React + Vite   │────▶│  FastAPI        │────▶│  Claude API     │
│  TailwindCSS    │     │  Python 3.11    │     │  Sonnet 4       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     Frontend               Backend              AI Generation
     (Vercel)            (Railway/Render)
```

### Key Technical Decisions

- **Claude for Generation**: Uses structured prompts with healthcare context to generate technically accurate architectures
- **Mermaid.js for Diagrams**: Code-based diagrams that render consistently and export cleanly
- **FastAPI Backend**: Clean async handling for Claude API calls with proper error handling
- **TypeScript Frontend**: Strong typing prevents runtime errors, improves maintainability

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Anthropic API key

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
echo "ANTHROPIC_API_KEY=your-key" > .env
uvicorn app.main:app --reload
```

### Environment Variables

**Frontend** (`.env`)
```
VITE_API_URL=http://localhost:8000
```

**Backend** (`.env`)
```
ANTHROPIC_API_KEY=sk-ant-...
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
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Claude integration
│   │   └── models/         # Request/response models
│   ├── prompts/            # Claude prompt templates
│   └── requirements.txt
├── docs/
│   ├── PRD.md              # Product requirements
│   └── ARCHITECTURE.md     # Technical details
├── CLAUDE.md               # Development context (Claude Code)
└── README.md               # This file
```

## Healthcare Domain Expertise

This tool embeds deep healthcare IT knowledge:

### HIPAA Compliance
- Administrative, physical, and technical safeguards
- BAA requirements for cloud services and Anthropic API
- Minimum necessary principle for PHI access

### Integration Patterns
- EHR systems (Epic, Cerner) via FHIR APIs
- Payer systems via X12 EDI transactions
- Clinical coding systems (ICD-10, CPT)

### Cloud Healthcare Services
- AWS HealthLake, Comprehend Medical
- GCP Healthcare API, Vertex AI

## Contributing

This is a portfolio project, but feedback is welcome! Open an issue or reach out on [LinkedIn](https://linkedin.com/in/edgaile).

## About

Built by [Ed Gaile](https://linkedin.com/in/edgaile) as a portfolio project demonstrating Partner Solutions Architect capabilities—technical depth, strategic thinking, and practical partner enablement value.

### Why I Built This

After 25+ years in enterprise solutions—including healthcare IT implementations for Blue Shield, CIGNA, BCBS, and Novartis—I understand the challenges GSI partners face when deploying AI solutions in regulated industries. This tool addresses those challenges while demonstrating how Claude can be used to build tools that help partners succeed with Claude.

---

*Built with Claude Code and Claude Sonnet 4*
