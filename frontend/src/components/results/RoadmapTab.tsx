import { Calendar, CheckCircle2 } from 'lucide-react';
import type { RoadmapPhase } from '../../lib/insights';

interface RoadmapTabProps {
  phases: RoadmapPhase[];
}

export function RoadmapTab({ phases }: RoadmapTabProps) {
  return (
    <div className="space-y-4">
      {phases.map((phase, index) => (
        <div key={phase.phase} className="card p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-anthropic-100 font-semibold text-anthropic-700">
                {index}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{phase.phase}</h3>
                <p className="mt-1 text-sm leading-relaxed text-gray-600">{phase.objective}</p>
              </div>
            </div>
            <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
              <Calendar className="h-3.5 w-3.5" />
              {phase.timeline}
            </span>
          </div>

          <div className="mt-5 grid gap-5 lg:grid-cols-2">
            <div>
              <p className="mb-3 text-sm font-semibold text-gray-900">Key Activities</p>
              <ul className="space-y-2">
                {phase.activities.map((activity, activityIndex) => (
                  <li key={activityIndex} className="text-sm leading-relaxed text-gray-700">
                    {activity}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="mb-3 text-sm font-semibold text-gray-900">Exit Criteria</p>
              <ul className="space-y-2">
                {phase.exitCriteria.map((criteria, criteriaIndex) => (
                  <li key={criteriaIndex} className="flex gap-2 text-sm leading-relaxed text-gray-700">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-600" />
                    <span>{criteria}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
