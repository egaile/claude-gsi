import { Layers, Shield, Rocket, Code, ArrowLeft, Download } from 'lucide-react';
import { Tabs } from './Tabs';
import { ArchitectureTab } from './ArchitectureTab';
import { ComplianceTab } from './ComplianceTab';
import { DeploymentTab } from './DeploymentTab';
import { CodeTab } from './CodeTab';
import type {
  ArchitectureRequest,
  Architecture,
  Compliance,
  Deployment,
  SampleCode
} from '../../lib/types';
import { downloadFile } from '../../lib/utils';

interface ResultsDashboardProps {
  architecture?: Architecture;
  compliance?: Compliance;
  deployment?: Deployment;
  sampleCode?: SampleCode;
  request: ArchitectureRequest;
  onReset: () => void;
  onGenerateCode?: () => void;
  codeLoading?: boolean;
  isStreaming?: boolean;
}

function LoadingSkeleton({ label }: { label: string }) {
  return (
    <div className="animate-pulse space-y-4">
      <div className="flex items-center gap-2 text-gray-500">
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <span>Loading {label}...</span>
      </div>
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      <div className="h-32 bg-gray-200 rounded"></div>
    </div>
  );
}

export function ResultsDashboard({
  architecture,
  compliance,
  deployment,
  sampleCode,
  request,
  onReset,
  onGenerateCode,
  codeLoading,
  isStreaming
}: ResultsDashboardProps) {
  const tabs = [
    {
      id: 'architecture',
      label: 'Architecture',
      icon: <Layers className="w-4 h-4" />,
      loading: !architecture
    },
    {
      id: 'compliance',
      label: 'Compliance',
      icon: <Shield className="w-4 h-4" />,
      loading: !compliance
    },
    {
      id: 'deployment',
      label: 'Deployment',
      icon: <Rocket className="w-4 h-4" />,
      loading: !deployment
    },
    {
      id: 'code',
      label: 'Code',
      icon: <Code className="w-4 h-4" />,
      loading: codeLoading
    },
  ];

  const handleExportMarkdown = () => {
    if (!architecture || !compliance || !deployment) return;
    const markdown = generateMarkdown(
      { architecture, compliance, deployment, sampleCode },
      request
    );
    downloadFile(markdown, 'architecture-reference.md', 'text/markdown');
  };

  const canExport = architecture && compliance && deployment;

  return (
    <div className="card p-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-gray-900">Generated Architecture</h2>
          {isStreaming && (
            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium bg-anthropic-100 text-anthropic-700">
              <span className="w-2 h-2 bg-anthropic-500 rounded-full animate-pulse"></span>
              Streaming
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportMarkdown}
            disabled={!canExport}
            className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            Export Markdown
          </button>
          <button onClick={onReset} className="btn-secondary flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            New Architecture
          </button>
        </div>
      </div>

      <Tabs tabs={tabs} defaultTab="architecture">
        {(activeTab) => {
          switch (activeTab) {
            case 'architecture':
              return architecture ? (
                <ArchitectureTab architecture={architecture} />
              ) : (
                <LoadingSkeleton label="architecture diagram" />
              );
            case 'compliance':
              return compliance ? (
                <ComplianceTab compliance={compliance} />
              ) : (
                <LoadingSkeleton label="compliance checklist" />
              );
            case 'deployment':
              return deployment ? (
                <DeploymentTab deployment={deployment} />
              ) : (
                <LoadingSkeleton label="deployment guide" />
              );
            case 'code':
              return (
                <CodeTab
                  sampleCode={sampleCode}
                  onGenerateCode={onGenerateCode}
                  isLoading={codeLoading}
                />
              );
            default:
              return null;
          }
        }}
      </Tabs>
    </div>
  );
}

interface PartialResponse {
  architecture?: Architecture;
  compliance?: Compliance;
  deployment?: Deployment;
  sampleCode?: SampleCode;
}

function generateMarkdown(response: PartialResponse, request: ArchitectureRequest): string {
  const { architecture, compliance, deployment, sampleCode } = response;
  const timestamp = new Date().toISOString();

  if (!architecture || !compliance || !deployment) {
    return '# Architecture generation incomplete';
  }

  let markdown = `# Generated Reference Architecture

> **Generated**: ${timestamp}
>
> **Configuration**:
> - Use Case: ${request.useCase}
> - Cloud Platform: ${request.cloudPlatform}
> - Integration Pattern: ${request.integrationPattern}
> - Data Classification: ${request.dataClassification}
> - Scale Tier: ${request.scaleTier}

## Architecture Diagram

\`\`\`mermaid
${architecture.mermaidDiagram}
\`\`\`

## Components

| Component | Service | Purpose | PHI Touchpoint |
|-----------|---------|---------|----------------|
${architecture.components.map((c) => `| ${c.name} | ${c.service} | ${c.purpose} | ${c.phiTouchpoint ? 'Yes' : 'No'} |`).join('\n')}

## Data Flows

${architecture.dataFlows.map((f) => `- **${f.from}** → **${f.to}**: ${f.data} ${f.encrypted ? '(Encrypted)' : ''}`).join('\n')}

## HIPAA Compliance

### BAA Requirements
${compliance.baaRequirements}

### Compliance Checklist

${['administrative', 'physical', 'technical'].map((category) => {
  const items = compliance.checklist.filter((item) => item.category === category);
  if (items.length === 0) return '';
  return `#### ${category.charAt(0).toUpperCase() + category.slice(1)} Safeguards

${items.map((item) => `- **${item.requirement}** (${item.priority})
  - ${item.implementation}`).join('\n')}`;
}).filter(Boolean).join('\n\n')}

## Deployment Guide

### Steps
${deployment.steps.map((step, i) => `${i + 1}. ${step}`).join('\n')}

### IAM Policies
${deployment.iamPolicies.map((policy) => `\`\`\`json\n${policy}\n\`\`\``).join('\n\n')}

### Network Configuration
\`\`\`
${deployment.networkConfig}
\`\`\`

### Monitoring Setup
${deployment.monitoringSetup}
`;

  if (sampleCode) {
    markdown += `
## Sample Code

### Python
\`\`\`python
${sampleCode.python}
\`\`\`

### TypeScript
\`\`\`typescript
${sampleCode.typescript}
\`\`\`
`;
  } else {
    markdown += `
## Sample Code

*Sample code not generated. Use the "Generate Sample Code" button in the application to generate code examples.*
`;
  }

  markdown += `
---
*Generated by Reference Architecture Generator*
`;

  return markdown;
}
