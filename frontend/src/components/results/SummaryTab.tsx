import { CheckCircle, FileText, Lightbulb, Target } from 'lucide-react';
import type { ExecutiveSummary } from '../../lib/insights';

interface SummaryTabProps {
  summary: ExecutiveSummary;
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="space-y-3">
      {items.map((item, index) => (
        <li key={index} className="flex gap-2 text-sm leading-relaxed text-gray-700">
          <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-600" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function SummaryTab({ summary }: SummaryTabProps) {
  return (
    <div className="space-y-6">
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="mb-3 flex items-center gap-2 font-semibold text-blue-950">
          <FileText className="h-5 w-5" />
          Executive Summary
        </h3>
        <p className="text-xl font-semibold leading-snug text-gray-950">
          {summary.headline}
        </p>
        <p className="mt-3 leading-relaxed text-blue-900">{summary.overview}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
            <Target className="h-5 w-5" />
            Business Value
          </h3>
          <BulletList items={summary.businessValue} />
        </div>

        <div className="card p-6">
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
            <Lightbulb className="h-5 w-5" />
            Implementation Focus
          </h3>
          <BulletList items={summary.implementationFocus} />
        </div>
      </div>

      <div className="card p-6">
        <h3 className="mb-4 font-semibold text-gray-900">Recommended Next Steps</h3>
        <div className="grid gap-3 md:grid-cols-3">
          {summary.nextSteps.map((step, index) => (
            <div key={index} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="mb-2 flex h-7 w-7 items-center justify-center rounded-full bg-anthropic-100 text-sm font-semibold text-anthropic-700">
                {index + 1}
              </div>
              <p className="text-sm leading-relaxed text-gray-700">{step}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
