import type {
  Architecture,
  ArchitectureRequest,
  Compliance,
  Deployment,
} from './types';

export interface ExecutiveSummary {
  headline: string;
  overview: string;
  businessValue: string[];
  implementationFocus: string[];
  nextSteps: string[];
}

export interface RoadmapPhase {
  phase: string;
  timeline: string;
  objective: string;
  activities: string[];
  exitCriteria: string[];
}

export interface RiskItem {
  risk: string;
  impact: 'High' | 'Medium' | 'Low';
  likelihood: 'High' | 'Medium' | 'Low';
  mitigation: string;
  owner: string;
}

const USE_CASE_LABELS: Record<string, string> = {
  'clinical-documentation': 'clinical documentation assistance',
  'prior-authorization': 'prior authorization automation',
  'medical-coding': 'medical coding support',
  'patient-communication': 'patient communication',
};

const CLOUD_LABELS: Record<string, string> = {
  'aws-bedrock': 'AWS',
  'gcp-vertex': 'Google Cloud',
};

const PROVIDER_LABELS: Record<string, string> = {
  claude: 'Claude',
  openai: 'OpenAI ChatGPT',
};

const SCALE_LABELS: Record<string, string> = {
  pilot: 'pilot',
  production: 'production',
  enterprise: 'enterprise',
};

function labelFor(value: string, labels: Record<string, string>): string {
  return labels[value] || value;
}

export function buildExecutiveSummary(
  request: ArchitectureRequest,
  architecture: Architecture,
  compliance: Compliance,
  deployment: Deployment
): ExecutiveSummary {
  const useCase = labelFor(request.useCase, USE_CASE_LABELS);
  const cloud = labelFor(request.cloudPlatform, CLOUD_LABELS);
  const provider = labelFor(request.aiProvider, PROVIDER_LABELS);
  const scale = labelFor(request.scaleTier, SCALE_LABELS);
  const phiComponents = architecture.components.filter((component) => component.phiTouchpoint);
  const requiredControls = compliance.checklist.filter((item) => item.priority === 'required');

  return {
    headline: `${provider} ${useCase} architecture on ${cloud}`,
    overview: `This reference architecture outlines a ${scale} healthcare AI implementation using ${provider} for ${useCase}. It identifies the application, AI, data, compliance, deployment, and monitoring considerations needed to move from discovery into implementation planning.`,
    businessValue: [
      'Accelerates early solution design for GSI pre-sales and delivery teams.',
      'Creates a repeatable healthcare AI pattern that can be adapted for customer-specific systems and controls.',
      'Surfaces PHI touchpoints, BAA considerations, and operational controls before implementation begins.',
      `Aligns cloud services, AI provider integration, and ${request.integrationPattern.replace('-', ' ')} delivery patterns in one customer-ready view.`,
    ],
    implementationFocus: [
      `${architecture.components.length} architecture components identified, including ${phiComponents.length} PHI touchpoints.`,
      `${architecture.dataFlows.length} data flows documented, with encryption expectations captured in the architecture output.`,
      `${requiredControls.length} required compliance controls identified across administrative, physical, and technical safeguards.`,
      `${deployment.steps.length} deployment steps generated for infrastructure, security, monitoring, and rollout planning.`,
    ],
    nextSteps: [
      'Validate selected model, region, retention settings, and BAA coverage with the AI provider and cloud provider.',
      'Run a customer architecture review to confirm EHR, identity, network, and audit integration assumptions.',
      'Convert the generated roadmap into a delivery backlog with owners, environments, and acceptance criteria.',
    ],
  };
}

export function buildRoadmap(
  request: ArchitectureRequest,
  architecture: Architecture,
  compliance: Compliance
): RoadmapPhase[] {
  const hasPhi = request.dataClassification === 'phi' ||
    architecture.components.some((component) => component.phiTouchpoint);
  const requiredControls = compliance.checklist
    .filter((item) => item.priority === 'required')
    .slice(0, 3)
    .map((item) => item.requirement);

  return [
    {
      phase: 'Phase 0: Discovery and Controls',
      timeline: '1-2 weeks',
      objective: 'Confirm business scope, data sensitivity, and implementation guardrails.',
      activities: [
        'Validate target workflow, users, source systems, and success metrics.',
        'Confirm PHI/PII classification, BAA requirements, model availability, and data retention posture.',
        'Document integration assumptions for identity, network, EHR/FHIR, logging, and support operations.',
      ],
      exitCriteria: [
        'Approved architecture assumptions',
        hasPhi ? 'PHI handling and BAA checklist reviewed' : 'Data classification reviewed',
        'Pilot success metrics agreed',
      ],
    },
    {
      phase: 'Phase 1: Pilot Build',
      timeline: '3-5 weeks',
      objective: 'Deliver a constrained implementation that proves workflow value and technical feasibility.',
      activities: [
        'Deploy secure ingress, orchestration, provider invocation, and audit logging components.',
        'Implement prompt templates, output validation, error handling, and human review checkpoints.',
        'Connect representative test data and run workflow validation with a small user group.',
      ],
      exitCriteria: [
        'End-to-end workflow demonstrated',
        'Security and audit events captured',
        'Pilot users approve output quality thresholds',
      ],
    },
    {
      phase: 'Phase 2: Production Hardening',
      timeline: '4-8 weeks',
      objective: 'Prepare the solution for controlled production release.',
      activities: [
        'Harden IAM, networking, secrets, observability, rate limits, and disaster recovery procedures.',
        'Complete compliance evidence collection and operational runbooks.',
        ...requiredControls.map((control) => `Validate control: ${control}.`),
      ],
      exitCriteria: [
        'Production readiness review complete',
        'Monitoring and incident response runbooks approved',
        'Clinical/business owner sign-off captured',
      ],
    },
    {
      phase: 'Phase 3: Scale and Governance',
      timeline: 'Ongoing',
      objective: 'Expand adoption while controlling risk, cost, and model behavior.',
      activities: [
        'Roll out to additional teams, workflows, or regions using the validated pattern.',
        'Track cost, latency, usage, quality, drift signals, and support tickets.',
        'Establish governance cadence for model updates, prompt changes, policy changes, and audit reviews.',
      ],
      exitCriteria: [
        'Operating metrics reviewed on a defined cadence',
        'Reusable implementation pattern published',
        'Expansion backlog prioritized',
      ],
    },
  ];
}

export function buildRiskRegister(
  request: ArchitectureRequest,
  architecture: Architecture,
  compliance: Compliance
): RiskItem[] {
  const hasPhi = request.dataClassification === 'phi' ||
    architecture.components.some((component) => component.phiTouchpoint);
  const hasRequiredCompliance = compliance.checklist.some((item) => item.priority === 'required');

  const risks: RiskItem[] = [
    {
      risk: 'Sensitive data exposure',
      impact: hasPhi ? 'High' : 'Medium',
      likelihood: hasPhi ? 'Medium' : 'Low',
      mitigation: 'Apply minimum necessary data sharing, encryption, provider BAA validation, secrets management, and audit logging before production use.',
      owner: 'Security / Privacy',
    },
    {
      risk: 'Unreviewed AI output enters clinical or operational workflow',
      impact: 'High',
      likelihood: 'Medium',
      mitigation: 'Require human review, output validation, attestation capture, and clear workflow boundaries for all AI-generated content.',
      owner: 'Clinical / Business Owner',
    },
    {
      risk: 'Provider or model configuration changes affect output quality',
      impact: 'Medium',
      likelihood: 'Medium',
      mitigation: 'Version prompts, model settings, and evaluation examples; require regression testing before provider/model changes.',
      owner: 'AI Platform',
    },
    {
      risk: 'Audit evidence is incomplete',
      impact: hasRequiredCompliance ? 'High' : 'Medium',
      likelihood: 'Medium',
      mitigation: 'Log request metadata, access decisions, provider invocation IDs, review actions, and operational events without storing raw PHI in logs.',
      owner: 'Compliance / Operations',
    },
    {
      risk: 'Latency or cost exceeds production expectations',
      impact: request.scaleTier === 'enterprise' ? 'High' : 'Medium',
      likelihood: request.scaleTier === 'pilot' ? 'Low' : 'Medium',
      mitigation: 'Define usage budgets, rate limits, caching strategy, token monitoring, and escalation paths before rollout.',
      owner: 'Platform / FinOps',
    },
  ];

  if (request.integrationPattern === 'event-driven' || request.integrationPattern === 'batch-processing') {
    risks.push({
      risk: 'Asynchronous workflow failures delay downstream operations',
      impact: 'Medium',
      likelihood: 'Medium',
      mitigation: 'Add dead-letter queues, replay procedures, idempotency keys, and operator alerts for stalled or failed work items.',
      owner: 'Engineering / Operations',
    });
  }

  return risks;
}
