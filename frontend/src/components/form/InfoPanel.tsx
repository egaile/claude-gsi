import { CheckCircle, Cpu } from 'lucide-react';

export function InfoPanel() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-3">What You'll Get</h3>
        <ul className="space-y-3 text-sm text-gray-600">
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Architecture diagram with PHI touchpoints highlighted</span>
          </li>
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>HIPAA compliance checklist specific to your use case</span>
          </li>
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Cloud-specific deployment guide with IAM policies</span>
          </li>
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Sample integration code in Python and TypeScript</span>
          </li>
        </ul>
      </div>

      <div className="card p-6 bg-anthropic-50 border-anthropic-200">
        <h3 className="font-semibold text-anthropic-900 mb-2 flex items-center gap-2">
          <Cpu className="w-5 h-5" />
          Powered by Claude
        </h3>
        <p className="text-sm text-anthropic-700">
          This tool uses Claude to generate architectures—demonstrating the product
          while building tools that help partners succeed with Claude.
        </p>
      </div>
    </div>
  );
}
