# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context7 Integration

Always use Context7 when code generation, setup or configuration steps, or library/API documentation is needed. Automatically use the Context7 MCP tools to resolve library IDs and get library docs without requiring explicit requests.

## Project Overview

GSI Reference Architecture Generator - A tool that uses Claude to generate healthcare-specific deployment architectures for Global System Integrator (GSI) partners. Demonstrates the product while building tools to help partners sell it.

## Development Commands

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev          # Dev server on port 5173
npm run build        # TypeScript compile + production build
npm run lint         # ESLint check
npm run preview      # Preview production build
```

### Backend (Python + FastAPI)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Code quality
black .              # Format code
ruff check .         # Lint

# Tests
pytest               # Run all tests
pytest -x            # Stop on first failure
```

## Architecture

**Frontend** → **Backend** → **Claude API**

### Backend Flow
1. `app/main.py` - FastAPI entry, CORS config, `/api/generate-architecture` endpoint
2. `app/models.py` - Pydantic request/response models with camelCase aliases
3. `app/services/generator.py` - `ArchitectureGenerator` class orchestrates prompt building and Claude calls

### Prompt Assembly
The generator builds prompts from files in `backend/prompts/`:
- `system_prompt.txt` - Base system prompt (healthcare IT architect persona)
- `healthcare_context.txt` - HIPAA/PHI handling context
- `aws_bedrock_context.txt` / `gcp_vertex_context.txt` - Cloud-specific services
- `templates/example_output.md` - Example JSON structure for few-shot guidance

### Frontend State
`App.tsx` manages `GenerationState` (idle → loading → success/error) and `ArchitectureRequest` form data. API client in `src/lib/api.ts`.

## Key Technical Details

- **Model**: Uses `claude-sonnet-4-20250514` in `generator.py:25`
- **Response parsing**: Claude returns raw JSON; generator strips markdown fences if present
- **CORS**: Configured via `CORS_ORIGINS` env var (comma-separated)
- **Pydantic aliases**: Models use `Field(alias="camelCase")` with `populate_by_name = True`

## Environment Variables

**Frontend** `.env`:
```
VITE_API_URL=http://localhost:8000
```

**Backend** `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
CORS_ORIGINS=http://localhost:5173
```

## API Endpoint

`POST /api/generate-architecture`

Request selects: use case, cloud platform, integration pattern, data classification, scale tier.

Response includes: Mermaid diagram, components with PHI touchpoints, HIPAA compliance checklist, deployment steps, sample code (Python/TypeScript).

See `backend/app/models.py` for full schema.
