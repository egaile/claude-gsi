# Development Guide

## GSI Reference Architecture Generator

This guide covers local development setup, project structure, and how to extend the application.

---

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Anthropic API Key** from [console.anthropic.com](https://console.anthropic.com)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/egaile/claude-gsi.git
cd claude-gsi
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Verify VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

---

## Project Structure

```
gsi-reference-architecture/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ui/             # Reusable UI primitives
│   │   │   ├── layout/         # Header, Footer
│   │   │   ├── form/           # Configuration form
│   │   │   └── results/        # Results dashboard, tabs
│   │   ├── lib/                # Utilities, API client, types
│   │   ├── styles/             # Global CSS, Tailwind
│   │   ├── App.tsx             # Root component
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # FastAPI app, endpoints
│   │   ├── models.py           # Pydantic models
│   │   └── services/
│   │       └── generator.py    # Claude integration
│   ├── prompts/                # Context files for Claude
│   ├── templates/              # Example output
│   └── requirements.txt
├── docs/                       # Documentation
├── CLAUDE.md                   # Claude Code guidance
└── README.md                   # Project overview
```

---

## Development Commands

### Frontend

```bash
npm run dev        # Start dev server with hot reload
npm run build      # TypeScript compile + production build
npm run preview    # Preview production build locally
npm run lint       # Run ESLint
```

### Backend

```bash
uvicorn app.main:app --reload    # Start with auto-reload
black .                          # Format Python code
ruff check .                     # Lint Python code
pytest                           # Run tests
pytest -x                        # Stop on first failure
```

---

## Code Style

### TypeScript/React

- Functional components with hooks
- Strong typing (no `any`)
- Named exports for components
- Use `cn()` utility for conditional classes

```typescript
// Good
export function MyComponent({ title }: { title: string }) {
  return <h1 className={cn('text-lg', isActive && 'font-bold')}>{title}</h1>;
}

// Avoid
export default function MyComponent({ title }: any) { ... }
```

### Python

- Type hints on all functions
- Pydantic models for validation
- Async functions for I/O
- Docstrings on public functions

```python
# Good
async def generate(self, request: ArchitectureRequest) -> ArchitectureResponse:
    """Generate architecture using Claude."""
    ...

# Avoid
def generate(self, request):
    ...
```

---

## Adding a New Use Case

To add a new healthcare use case (e.g., "radiology-reporting"):

### 1. Update Backend Types

Edit `backend/app/models.py`:

```python
class UseCase(str, Enum):
    CLINICAL_DOCUMENTATION = "clinical-documentation"
    PRIOR_AUTHORIZATION = "prior-authorization"
    MEDICAL_CODING = "medical-coding"
    PATIENT_COMMUNICATION = "patient-communication"
    RADIOLOGY_REPORTING = "radiology-reporting"  # Add new case
```

### 2. Add Use Case Context

Edit `backend/app/services/generator.py` in the `_get_use_case_context` method:

```python
UseCase.RADIOLOGY_REPORTING: """
## Use Case: Radiology Reporting

### Integration Points
- PACS (Picture Archiving and Communication System)
- RIS (Radiology Information System)
- Speech recognition systems (PowerScribe, Nuance)

### PHI Considerations
- Patient demographics
- Imaging studies and reports
- Referring physician information

### Specific Compliance Requirements
- Image data handling and storage
- Report authentication and signing
- Turnaround time tracking
""",
```

### 3. Update Frontend Types

Edit `frontend/src/lib/types.ts`:

```typescript
export type UseCase =
  | 'clinical-documentation'
  | 'prior-authorization'
  | 'medical-coding'
  | 'patient-communication'
  | 'radiology-reporting';  // Add new case

export const USE_CASE_OPTIONS: Record<UseCase, { label: string; description: string }> = {
  // ... existing options
  'radiology-reporting': {
    label: 'Radiology Reporting',
    description: 'AI-assisted radiology report generation and analysis',
  },
};
```

### 4. Test

Generate an architecture with the new use case and verify the output is appropriate.

---

## Adding a New Cloud Platform

To add a new cloud platform (e.g., Azure):

### 1. Create Context File

Create `backend/prompts/azure_openai_context.txt`:

```text
## Azure Cloud Platform Context

### Core AI Services
- Azure OpenAI Service: Claude models via Azure
- Azure Health Data Services: FHIR server
- Azure Cognitive Services: Healthcare NLP

### Integration Patterns
...
```

### 2. Update Backend Types

Edit `backend/app/models.py`:

```python
class CloudPlatform(str, Enum):
    AWS_BEDROCK = "aws-bedrock"
    GCP_VERTEX = "gcp-vertex"
    AZURE_OPENAI = "azure-openai"  # Add new platform
```

### 3. Update Generator

Edit `backend/app/services/generator.py`:

```python
def __init__(self, api_key: str):
    # ... existing code
    self.azure_context = self._load_prompt("azure_openai_context.txt")

def _get_cloud_context(self, platform: CloudPlatform) -> str:
    if platform == CloudPlatform.AWS_BEDROCK:
        return self.aws_context
    elif platform == CloudPlatform.AZURE_OPENAI:
        return self.azure_context
    return self.gcp_context
```

### 4. Update Frontend Types

Edit `frontend/src/lib/types.ts`:

```typescript
export type CloudPlatform = 'aws-bedrock' | 'gcp-vertex' | 'azure-openai';

export const CLOUD_PLATFORM_OPTIONS: Record<CloudPlatform, { label: string; description: string }> = {
  // ... existing options
  'azure-openai': {
    label: 'Azure OpenAI',
    description: 'Microsoft Azure with Claude models',
  },
};
```

---

## Prompt Engineering

The quality of generated architectures depends heavily on the prompts. Key files:

### System Prompt (`prompts/system_prompt.txt`)

Establishes Claude's persona and expertise:
- Healthcare IT architecture
- HIPAA compliance
- Cloud deployment patterns

### Healthcare Context (`prompts/healthcare_context.txt`)

Domain knowledge:
- HIPAA Security Rule breakdown
- PHI categories
- BAA requirements

### Cloud Contexts (`prompts/aws_bedrock_context.txt`, `prompts/gcp_vertex_context.txt`)

Platform-specific services:
- Service catalogs
- Integration patterns
- Security configurations

### Example Output (`templates/example_output.md`)

Few-shot learning example showing the expected JSON structure.

### Tips for Prompt Modification

1. **Be specific**: Include exact service names and configuration details
2. **Use examples**: Add sample configurations and policies
3. **Test iteratively**: Small changes can significantly affect output
4. **Monitor token usage**: Longer prompts cost more

---

## Testing

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest tests/test_api.py  # Run specific test file
pytest -v                 # Verbose output
pytest -x                 # Stop on first failure
```

### Frontend Type Checking

```bash
cd frontend
npx tsc --noEmit          # Check types without building
```

### Manual Testing Checklist

- [ ] All 4 use cases generate successfully
- [ ] Both cloud platforms work
- [ ] All 3 integration patterns work
- [ ] All 4 data classifications work
- [ ] All 3 scale tiers work
- [ ] Mermaid diagram renders correctly
- [ ] Copy buttons work in all tabs
- [ ] Download buttons work in Code tab
- [ ] Export Markdown works
- [ ] Error states display correctly

---

## Debugging

### Backend Debugging

Add print statements or use Python debugger:

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

Or use VS Code's Python debugger with launch.json:

```json
{
  "name": "FastAPI",
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["app.main:app", "--reload"]
}
```

### Frontend Debugging

Use browser DevTools:
- React DevTools for component inspection
- Network tab for API requests
- Console for errors

### Common Issues

**Claude returns incomplete JSON**:
- Increase `max_tokens` in `generator.py`
- Simplify the prompt to reduce response size

**Mermaid fails to render**:
- Check for special characters in node names
- View raw diagram in error fallback

**CORS errors**:
- Verify `CORS_ORIGINS` environment variable
- Check for trailing slashes in URLs

---

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Ensure code passes linting: `npm run lint` and `ruff check .`
4. Commit with descriptive message
5. Push and create pull request

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Mermaid Documentation](https://mermaid.js.org)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security)
