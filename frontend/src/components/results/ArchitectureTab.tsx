import { ArrowRight, Lock, Shield } from 'lucide-react';
import { MermaidDiagram } from '../ui/MermaidDiagram';
import { CopyButton } from '../ui/CopyButton';
import { Badge } from '../ui/Badge';
import type { Architecture } from '../../lib/types';

interface ArchitectureTabProps {
  architecture: Architecture;
}

export function ArchitectureTab({ architecture }: ArchitectureTabProps) {
  return (
    <div className="space-y-8">
      {/* Diagram Section */}
      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Architecture Diagram</h3>
          <CopyButton text={architecture.mermaidDiagram} label="Copy Mermaid" />
        </div>
        <MermaidDiagram diagram={architecture.mermaidDiagram} />
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
