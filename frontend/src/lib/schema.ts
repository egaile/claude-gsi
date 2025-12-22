import { z } from 'zod';

// Response validation schemas using Zod for runtime type checking

export const ArchitectureComponentSchema = z.object({
  name: z.string(),
  service: z.string(),
  purpose: z.string(),
  phiTouchpoint: z.boolean(),
});

export const DataFlowSchema = z.object({
  from: z.string(),
  to: z.string(),
  data: z.string(),
  encrypted: z.boolean(),
});

export const ComplianceItemSchema = z.object({
  category: z.enum(['administrative', 'physical', 'technical']),
  requirement: z.string(),
  implementation: z.string(),
  priority: z.enum(['required', 'recommended', 'addressable']),
});

export const ArchitectureSchema = z.object({
  mermaidDiagram: z.string(),
  components: z.array(ArchitectureComponentSchema),
  dataFlows: z.array(DataFlowSchema),
});

export const ComplianceSchema = z.object({
  checklist: z.array(ComplianceItemSchema),
  baaRequirements: z.string(),
});

// IAM policy can be a string (JSON) or any object structure
// Claude returns various formats, so we accept anything and handle display in the component
export const IamPolicySchema = z.union([
  z.string(),
  z.record(z.string(), z.unknown()),
]);

export const DeploymentSchema = z.object({
  steps: z.array(z.string()),
  iamPolicies: z.array(IamPolicySchema),
  networkConfig: z.string(),
  monitoringSetup: z.string(),
});

export const SampleCodeSchema = z.object({
  python: z.string(),
  typescript: z.string(),
});

export const ArchitectureResponseSchema = z.object({
  architecture: ArchitectureSchema,
  compliance: ComplianceSchema,
  deployment: DeploymentSchema,
  sampleCode: SampleCodeSchema,
});

// Partial response schema (without sampleCode) for streaming
export const ArchitectureResponsePartialSchema = z.object({
  architecture: ArchitectureSchema,
  compliance: ComplianceSchema,
  deployment: DeploymentSchema,
});

// Code generation response schema
export const CodeGenerationResponseSchema = z.object({
  sampleCode: SampleCodeSchema,
});

export type ValidatedArchitectureResponse = z.infer<typeof ArchitectureResponseSchema>;
export type ValidatedArchitectureResponsePartial = z.infer<typeof ArchitectureResponsePartialSchema>;
export type ValidatedCodeGenerationResponse = z.infer<typeof CodeGenerationResponseSchema>;
