import { AlertTriangle } from 'lucide-react';
import { Badge } from '../ui/Badge';
import type { RiskItem } from '../../lib/insights';

interface RiskTabProps {
  risks: RiskItem[];
}

function severityVariant(value: RiskItem['impact'] | RiskItem['likelihood']) {
  if (value === 'High') return 'error';
  if (value === 'Medium') return 'warning';
  return 'success';
}

export function RiskTab({ risks }: RiskTabProps) {
  return (
    <div className="card p-6">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-amber-600" />
        <h3 className="font-semibold text-gray-900">Implementation Risk Register</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Risk</th>
              <th className="px-4 py-3 text-center font-medium text-gray-600">Impact</th>
              <th className="px-4 py-3 text-center font-medium text-gray-600">Likelihood</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Mitigation</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Owner</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {risks.map((risk, index) => (
              <tr key={index} className="align-top hover:bg-gray-50">
                <td className="px-4 py-4 font-medium text-gray-900">{risk.risk}</td>
                <td className="px-4 py-4 text-center">
                  <Badge variant={severityVariant(risk.impact)}>{risk.impact}</Badge>
                </td>
                <td className="px-4 py-4 text-center">
                  <Badge variant={severityVariant(risk.likelihood)}>{risk.likelihood}</Badge>
                </td>
                <td className="px-4 py-4 leading-relaxed text-gray-700">{risk.mitigation}</td>
                <td className="px-4 py-4 text-gray-700">{risk.owner}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
