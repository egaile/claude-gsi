import { useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  ArrowRight,
  BrainCircuit,
  Database,
  GitBranch,
  ListTree,
  Lock,
  Monitor,
  Network,
  Shield,
  ShieldCheck,
  Workflow,
} from 'lucide-react';
import { MermaidDiagram } from '../ui/MermaidDiagram';
import { CopyButton } from '../ui/CopyButton';
import { Badge } from '../ui/Badge';
import type { Architecture, ArchitectureComponent } from '../../lib/types';

interface ArchitectureTabProps {
  architecture: Architecture;
}

type DiagramMode = 'map' | 'simplified' | 'detailed';

interface ArchitectureLane {
  id: string;
  label: string;
  icon: ReactNode;
  components: ArchitectureComponent[];
}

function cleanLabel(label: string): string {
  return label
    .replace(/["[\]{}()]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 42);
}

function createNodeId(label: string, index: number): string {
  const id = label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 24);

  return id ? `${id}_${index}` : `node_${index}`;
}

function buildSimplifiedDiagram(architecture: Architecture): string {
  const nodeIds = new Map<string, string>();
  const componentsByName = new Map<string, ArchitectureComponent>();
  const lines = ['flowchart TD'];

  architecture.components.forEach((component, index) => {
    const id = createNodeId(component.name, index);
    nodeIds.set(component.name, id);
    componentsByName.set(component.name, component);
  });

  architecture.dataFlows.forEach((flow) => {
    if (!nodeIds.has(flow.from)) {
      nodeIds.set(flow.from, createNodeId(flow.from, nodeIds.size));
    }
    if (!nodeIds.has(flow.to)) {
      nodeIds.set(flow.to, createNodeId(flow.to, nodeIds.size));
    }
  });

  const phiNodes: string[] = [];
  const nonPhiNodes: string[] = [];

  nodeIds.forEach((id, name) => {
    const component = componentsByName.get(name);
    const nodeLine = `    ${id}["${cleanLabel(name)}"]`;
    if (component?.phiTouchpoint) {
      phiNodes.push(nodeLine);
    } else {
      nonPhiNodes.push(nodeLine);
    }
  });

  if (nonPhiNodes.length > 0) {
    lines.push('  subgraph control["Application and Control Plane"]');
    lines.push(...nonPhiNodes);
    lines.push('  end');
  }

  if (phiNodes.length > 0) {
    lines.push('  subgraph phi["PHI Processing Zone"]');
    lines.push(...phiNodes);
    lines.push('  end');
  }

  const edgeSet = new Set<string>();
  architecture.dataFlows.forEach((flow) => {
    const from = nodeIds.get(flow.from);
    const to = nodeIds.get(flow.to);
    if (!from || !to || from === to) return;

    const edge = `  ${from} --> ${to}`;
    if (!edgeSet.has(edge)) {
      edgeSet.add(edge);
      lines.push(edge);
    }
  });

  if (phiNodes.length > 0) {
    lines.push('  classDef phi fill:#fef3c7,stroke:#d97706,color:#111827');
    architecture.components.forEach((component) => {
      if (component.phiTouchpoint) {
        const id = nodeIds.get(component.name);
        if (id) lines.push(`  class ${id} phi`);
      }
    });
  }

  return lines.join('\n');
}

function classifyComponent(component: ArchitectureComponent): string {
  const text = `${component.name} ${component.service} ${component.purpose}`.toLowerCase();

  if (/ehr|epic|cerner|meditech|client|ui|portal|dictation|dragon|m\*modal/.test(text)) {
    return 'sources';
  }
  if (/api gateway|front door|waf|endpoint|ingress|authoriz|authenticat|throttl/.test(text)) {
    return 'access';
  }
  if (/openai|chatgpt|claude|llm|model|ai provider|bedrock|vertex/.test(text)) {
    return 'ai';
  }
  if (/s3|bucket|dynamodb|database|data store|healthlake|fhir|firestore|bigquery|storage|archive/.test(text)) {
    return 'data';
  }
  if (/secret|kms|key|cloudwatch|logging|monitor|audit|security|guardrail|policy/.test(text)) {
    return 'security';
  }

  return 'processing';
}

function buildLanes(components: ArchitectureComponent[]): ArchitectureLane[] {
  const lanes: ArchitectureLane[] = [
    {
      id: 'sources',
      label: 'Channels',
      icon: <Network className="h-4 w-4" />,
      components: [],
    },
    {
      id: 'access',
      label: 'Access',
      icon: <ShieldCheck className="h-4 w-4" />,
      components: [],
    },
    {
      id: 'processing',
      label: 'Workflow',
      icon: <Workflow className="h-4 w-4" />,
      components: [],
    },
    {
      id: 'ai',
      label: 'AI Provider',
      icon: <BrainCircuit className="h-4 w-4" />,
      components: [],
    },
    {
      id: 'data',
      label: 'Data Stores',
      icon: <Database className="h-4 w-4" />,
      components: [],
    },
    {
      id: 'security',
      label: 'Security and Ops',
      icon: <Monitor className="h-4 w-4" />,
      components: [],
    },
  ];
  const laneById = new Map(lanes.map((lane) => [lane.id, lane]));

  components.forEach((component) => {
    laneById.get(classifyComponent(component))?.components.push(component);
  });

  return lanes.filter((lane) => lane.components.length > 0);
}

function ArchitectureMap({ architecture }: { architecture: Architecture }) {
  const lanes = useMemo(() => buildLanes(architecture.components), [architecture.components]);

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-gray-50/80 p-4">
      <div
        className="grid min-w-[980px] gap-3"
        style={{ gridTemplateColumns: `repeat(${lanes.length}, minmax(150px, 1fr))` }}
      >
        {lanes.map((lane, laneIndex) => (
          <div key={lane.id} className="relative">
            {laneIndex < lanes.length - 1 && (
              <ArrowRight className="absolute -right-5 top-8 z-10 h-4 w-4 text-gray-300" />
            )}

            <div className="mb-3 flex items-center gap-2 border-b border-gray-200 pb-2 text-sm font-semibold text-gray-800">
              {lane.icon}
              {lane.label}
            </div>

            <div className="space-y-2">
              {lane.components.map((component, index) => (
                <div
                  key={`${lane.id}-${index}`}
                  className={`rounded-md border bg-white p-3 shadow-sm ${
                    component.phiTouchpoint
                      ? 'border-amber-200 ring-1 ring-amber-100'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold leading-snug text-gray-900">
                        {component.name}
                      </p>
                      <p className="mt-1 text-xs leading-snug text-gray-500">
                        {component.service}
                      </p>
                    </div>
                    {component.phiTouchpoint && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
                        PHI
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ArchitectureTab({ architecture }: ArchitectureTabProps) {
  const [diagramMode, setDiagramMode] = useState<DiagramMode>('map');
  const simplifiedDiagram = useMemo(
    () => buildSimplifiedDiagram(architecture),
    [architecture]
  );
  const activeDiagram =
    diagramMode === 'simplified' ? simplifiedDiagram : architecture.mermaidDiagram;

  return (
    <div className="space-y-8">
      {/* Diagram Section */}
      <div className="card p-6">
        <div className="flex flex-col gap-4 mb-4 sm:flex-row sm:items-center sm:justify-between">
          <h3 className="font-semibold text-gray-900">Architecture Diagram</h3>
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1">
              <button
                type="button"
                onClick={() => setDiagramMode('map')}
                className={`inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  diagramMode === 'map'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Network className="h-4 w-4" />
                Map
              </button>
              <button
                type="button"
                onClick={() => setDiagramMode('simplified')}
                className={`inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  diagramMode === 'simplified'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <GitBranch className="h-4 w-4" />
                Simplified
              </button>
              <button
                type="button"
                onClick={() => setDiagramMode('detailed')}
                className={`inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  diagramMode === 'detailed'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <ListTree className="h-4 w-4" />
                Detailed
              </button>
            </div>
            {diagramMode !== 'map' && (
              <CopyButton text={activeDiagram} label="Copy Mermaid" />
            )}
          </div>
        </div>
        {diagramMode === 'map' ? (
          <ArchitectureMap architecture={architecture} />
        ) : (
          <MermaidDiagram diagram={activeDiagram} />
        )}
      </div>

      {/* Components Table */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Components</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Component</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Service</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Purpose</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">PHI Touchpoint</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {architecture.components.map((component, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{component.name}</td>
                  <td className="px-4 py-3 text-gray-600">{component.service}</td>
                  <td className="px-4 py-3 text-gray-600">{component.purpose}</td>
                  <td className="px-4 py-3 text-center">
                    {component.phiTouchpoint ? (
                      <Badge variant="warning">
                        <Shield className="w-3 h-3" />
                        PHI
                      </Badge>
                    ) : (
                      <Badge variant="default">No</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Flows */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Data Flows</h3>
        <div className="space-y-3">
          {architecture.dataFlows.map((flow, i) => (
            <div
              key={i}
              className="flex flex-wrap items-center gap-3 p-3 bg-gray-50 rounded-lg"
            >
              <span className="font-medium text-gray-900">{flow.from}</span>
              <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <span className="font-medium text-gray-900">{flow.to}</span>
              <span className="text-gray-600 text-sm">({flow.data})</span>
              {flow.encrypted && (
                <Badge variant="success">
                  <Lock className="w-3 h-3" />
                  Encrypted
                </Badge>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
