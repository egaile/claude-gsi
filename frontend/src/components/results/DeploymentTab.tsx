import { Terminal, Shield, Network, Activity } from 'lucide-react';
import { CopyButton } from '../ui/CopyButton';
import type { Deployment, IamPolicy } from '../../lib/types';

interface DeploymentTabProps {
  deployment: Deployment;
}

// Helper to convert IAM policy to displayable string
function formatPolicy(policy: IamPolicy): string {
  if (typeof policy === 'string') {
    return policy;
  }
  // Object format - format as JSON
  return JSON.stringify(policy, null, 2);
}

// Helper to get policy name for display
function getPolicyName(policy: IamPolicy, index: number): string {
  if (typeof policy === 'string') {
    return `Policy ${index + 1}`;
  }
  return policy.name || `Policy ${index + 1}`;
}

export function DeploymentTab({ deployment }: DeploymentTabProps) {
  return (
    <div className="space-y-6">
      {/* Deployment Steps */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5" />
          Deployment Steps
        </h3>
        <ol className="list-decimal list-inside space-y-2">
          {deployment.steps.map((step, i) => (
            <li key={i} className="text-gray-700 leading-relaxed">
              {step}
            </li>
          ))}
        </ol>
      </div>

      {/* IAM Policies */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          IAM Policies
        </h3>
        <div className="space-y-4">
          {deployment.iamPolicies.map((policy, i) => {
            const formatted = formatPolicy(policy);
            const name = getPolicyName(policy, i);
            return (
              <div key={i} className="relative">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{name}</span>
                  <CopyButton text={formatted} />
                </div>
                <pre className="text-xs overflow-x-auto max-h-64">
                  <code>{formatted}</code>
                </pre>
              </div>
            );
          })}
        </div>
      </div>

      {/* Network Configuration */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Network className="w-5 h-5" />
          Network Configuration
        </h3>
        <div className="relative">
          <div className="absolute right-2 top-2 z-10">
            <CopyButton text={deployment.networkConfig} />
          </div>
          <pre className="text-xs overflow-x-auto pr-12 max-h-64">
            <code>{deployment.networkConfig}</code>
          </pre>
        </div>
      </div>

      {/* Monitoring Setup */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Monitoring Setup
        </h3>
        <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
          {deployment.monitoringSetup}
        </p>
      </div>
    </div>
  );
}
