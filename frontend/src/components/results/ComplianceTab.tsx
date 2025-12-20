import { FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';
import type { Compliance } from '../../lib/types';

interface ComplianceTabProps {
  compliance: Compliance;
}

const CATEGORY_ORDER = ['administrative', 'physical', 'technical'] as const;

const CATEGORY_LABELS: Record<string, string> = {
  administrative: 'Administrative Safeguards',
  physical: 'Physical Safeguards',
  technical: 'Technical Safeguards',
};

export function ComplianceTab({ compliance }: ComplianceTabProps) {
  return (
    <div className="space-y-6">
      {/* BAA Requirements */}
      <div className="card p-6 bg-anthropic-50 border-anthropic-200">
        <h3 className="font-semibold text-anthropic-900 mb-3 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Business Associate Agreement (BAA) Requirements
        </h3>
        <p className="text-anthropic-800 whitespace-pre-wrap">{compliance.baaRequirements}</p>
      </div>

      {/* Checklist by Category */}
      {CATEGORY_ORDER.map((category) => {
        const items = compliance.checklist.filter((item) => item.category === category);
        if (items.length === 0) return null;

        return (
          <div key={category} className="card p-6">
            <h3 className="font-semibold text-gray-900 mb-4">
              {CATEGORY_LABELS[category]}
            </h3>
            <div className="space-y-4">
              {items.map((item, i) => (
                <div
                  key={i}
                  className="border-l-4 border-gray-200 pl-4 hover:border-anthropic-400 transition-colors"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{item.requirement}</p>
                      <p className="text-sm text-gray-600 mt-1">{item.implementation}</p>
                    </div>
                    <div className="flex-shrink-0">
                      {item.priority === 'required' ? (
                        <Badge variant="error">
                          <AlertCircle className="w-3 h-3" />
                          Required
                        </Badge>
                      ) : (
                        <Badge variant="info">
                          <CheckCircle className="w-3 h-3" />
                          Recommended
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
