import { CheckCircle, Cpu } from 'lucide-react';

export function InfoPanel() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-3">What You'll Get</h3>
        <ul className="space-y-3 text-sm text-gray-600">
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Executive summary with business value and next steps</span>
          </li>
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Architecture map with PHI touchpoints highlighted</span>
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
            <span>Implementation roadmap and risk register for delivery planning</span>
          </li>
          <li className="flex gap-2">
            <CheckCircle className="w-5 h-5 text-anthropic-600 flex-shrink-0" />
            <span>Sample integration code in Python and TypeScript</span>
          </li>
        </ul>
      </div>

      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <Cpu className="w-5 h-5" />
          AI Provider Choice
        </h3>
        <p className="text-sm text-blue-700">
          Select Claude or OpenAI ChatGPT as the LLM provider while keeping the
          healthcare architecture, cloud deployment, and compliance guidance provider-neutral.
        </p>
      </div>
    </div>
  );
}
