// Configuration types
export type UseCase = 
  | 'clinical-documentation'
  | 'prior-authorization'
  | 'medical-coding'
  | 'patient-communication';

export type CloudPlatform = 'aws-bedrock' | 'gcp-vertex';

export type IntegrationPattern = 'api-gateway' | 'event-driven' | 'batch-processing';

export type DataClassification = 'phi' | 'pii' | 'de-identified' | 'public';

export type ScaleTier = 'pilot' | 'production' | 'enterprise';

export interface ArchitectureRequest {
  useCase: UseCase;
  cloudPlatform: CloudPlatform;
  integrationPattern: IntegrationPattern;
  dataClassification: DataClassification;
  scaleTier: ScaleTier;
}

// Response types
export interface ArchitectureComponent {
  name: string;
  service: string;
  purpose: string;
  phiTouchpoint: boolean;
}

export interface DataFlow {
  from: string;
  to: string;
  data: string;
  encrypted: boolean;
}

export interface ComplianceItem {
  category: 'administrative' | 'physical' | 'technical';
  requirement: string;
  implementation: string;
  priority: 'required' | 'recommended' | 'addressable';
}

export interface Architecture {
  mermaidDiagram: string;
  components: ArchitectureComponent[];
  dataFlows: DataFlow[];
}

export interface Compliance {
  checklist: ComplianceItem[];
  baaRequirements: string;
}

export interface Deployment {
  steps: string[];
  iamPolicies: string[];
  networkConfig: string;
  monitoringSetup: string;
}

export interface SampleCode {
  python: string;
  typescript: string;
}

export interface ArchitectureResponse {
  architecture: Architecture;
  compliance: Compliance;
  deployment: Deployment;
  sampleCode: SampleCode;
}

// Partial response (without sampleCode) for streaming
export interface ArchitectureResponsePartial {
  architecture: Architecture;
  compliance: Compliance;
  deployment: Deployment;
}

// Code generation types
export interface CodeGenerationRequest {
  useCase: UseCase;
  cloudPlatform: CloudPlatform;
  architectureSummary: string;
}

// UI state types
export interface GenerationState {
  status: 'idle' | 'loading' | 'success' | 'error';
  error?: string;
  response?: ArchitectureResponse;
}

// Streaming state - tracks which sections have loaded
export interface StreamingState {
  status: 'idle' | 'streaming' | 'success' | 'error';
  architecture?: Architecture;
  compliance?: Compliance;
  deployment?: Deployment;
  sampleCode?: SampleCode;
  codeLoading?: boolean;
  error?: string;
}

// Form configuration
export const USE_CASE_OPTIONS: Record<UseCase, { label: string; description: string }> = {
  'clinical-documentation': {
    label: 'Clinical Documentation',
    description: 'AI-assisted note generation and summarization for EHR systems',
  },
  'prior-authorization': {
    label: 'Prior Authorization',
    description: 'Streamline payer-provider authorization workflows',
  },
  'medical-coding': {
    label: 'Medical Coding',
    description: 'ICD-10 and CPT code suggestion and validation',
  },
  'patient-communication': {
    label: 'Patient Communication',
    description: 'Secure messaging, appointment prep, and follow-up',
  },
};

export const CLOUD_PLATFORM_OPTIONS: Record<CloudPlatform, { label: string; description: string }> = {
  'aws-bedrock': {
    label: 'AWS Bedrock',
    description: 'Amazon Bedrock with Claude models',
  },
  'gcp-vertex': {
    label: 'GCP Vertex AI',
    description: 'Google Cloud Vertex AI with Claude',
  },
};

export const INTEGRATION_PATTERN_OPTIONS: Record<IntegrationPattern, { label: string; description: string }> = {
  'api-gateway': {
    label: 'API Gateway',
    description: 'Synchronous REST/GraphQL API pattern',
  },
  'event-driven': {
    label: 'Event-Driven',
    description: 'Asynchronous message queue pattern',
  },
  'batch-processing': {
    label: 'Batch Processing',
    description: 'Scheduled bulk document processing',
  },
};

export const DATA_CLASSIFICATION_OPTIONS: Record<DataClassification, { label: string; description: string }> = {
  phi: {
    label: 'PHI',
    description: 'Protected Health Information - full compliance required',
  },
  pii: {
    label: 'PII',
    description: 'Personally Identifiable Information',
  },
  'de-identified': {
    label: 'De-identified',
    description: 'Data with identifiers removed per Safe Harbor',
  },
  public: {
    label: 'Public',
    description: 'Non-sensitive, publicly available data',
  },
};

export const SCALE_TIER_OPTIONS: Record<ScaleTier, { label: string; description: string }> = {
  pilot: {
    label: 'Pilot',
    description: 'Less than 100 users, proof of concept',
  },
  production: {
    label: 'Production',
    description: '100 to 10,000 users, full deployment',
  },
  enterprise: {
    label: 'Enterprise',
    description: '10,000+ users, high availability required',
  },
};
