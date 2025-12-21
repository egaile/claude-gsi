# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context7 Integration

Always use Context7 when code generation, setup or configuration steps, or library/API documentation is needed. Automatically use the Context7 MCP tools to resolve library IDs and get library docs without requiring explicit requests.

## Project Overview

Reference Architecture Generator - A tool that uses Claude to generate healthcare-specific deployment architectures. Demonstrates the product while building tools that help partners succeed with Claude.

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
1. `api/index.py` - Vercel serverless entry point with all endpoints
2. `app/models.py` - Pydantic request/response models with camelCase aliases
3. `app/services/generator.py` - `ArchitectureGenerator` class orchestrates prompt building and Claude calls

### API Endpoints
- `POST /api/generate-architecture` - Full generation (includes sample code)
- `POST /api/generate-architecture-stream` - SSE streaming (excludes sample code for faster response)
- `POST /api/generate-code` - On-demand code generation

### Prompt Assembly
The generator builds prompts from files in `backend/prompts/`:
- `system_prompt.txt` - Base system prompt (healthcare IT architect persona)
- `healthcare_context.txt` - HIPAA/PHI handling context
- `aws_bedrock_context.txt` / `gcp_vertex_context.txt` - Cloud-specific services
- `templates/example_output.md` - Example JSON structure for few-shot guidance

### Frontend State
`App.tsx` manages `StreamingState` (idle → streaming → success/error) with progressive section loading. Sections (architecture, compliance, deployment) load as they stream in; sample code is generated on-demand. API client in `src/lib/api.ts`.

## Key Technical Details

- **Model**: Uses `claude-sonnet-4-20250514` (configurable via `ANTHROPIC_MODEL` env var)
- **Streaming**: Uses SSE (Server-Sent Events) with `sse-starlette` for progressive response
- **Response parsing**: Claude returns raw JSON; generator strips markdown fences if present
- **CORS**: Configured via `CORS_ORIGINS` env var (comma-separated)
- **Rate limiting**: 10 requests/minute per IP (in-memory, resets on cold start)
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

## API Endpoints

### `POST /api/generate-architecture`
Full generation including sample code. Response time: ~90 seconds.

### `POST /api/generate-architecture-stream`
SSE streaming endpoint. Returns sections progressively (architecture → compliance → deployment). Excludes sample code for faster response (~45-50 seconds).

### `POST /api/generate-code`
On-demand code generation. Takes use case, cloud platform, and architecture summary. Returns Python and TypeScript samples (~30-40 seconds).

Request selects: use case, cloud platform, integration pattern, data classification, scale tier.

See `backend/app/models.py` and `api/index.py` for full schema.
