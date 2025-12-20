import { Terminal, Shield, Network, Activity } from 'lucide-react';
import { CopyButton } from '../ui/CopyButton';
import type { Deployment } from '../../lib/types';

interface DeploymentTabProps {
  deployment: Deployment;
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
          {deployment.iamPolicies.map((policy, i) => (
            <div key={i} className="relative">
              <div className="absolute right-2 top-2 z-10">
                <CopyButton text={policy} />
              </div>
              <pre className="text-xs overflow-x-auto pr-12 max-h-64">
                <code>{policy}</code>
              </pre>
            </div>
          ))}
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
