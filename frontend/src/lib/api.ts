import type {
  ArchitectureRequest,
  ArchitectureResponse,
  Architecture,
  Compliance,
  Deployment,
  SampleCode,
  CodeGenerationRequest
} from './types';
import {
  ArchitectureResponseSchema,
  ArchitectureSchema,
  ComplianceSchema,
  DeploymentSchema,
  SampleCodeSchema
} from './schema';

const API_URL = import.meta.env.VITE_API_URL || '';
const REQUEST_TIMEOUT_MS = 120000; // 2 minute timeout for generation requests
const HEALTH_CHECK_TIMEOUT_MS = 10000; // 10 second timeout for health checks

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Fetch with timeout support
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError('Request timeout - please try again', 408);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function generateArchitecture(
  request: ArchitectureRequest
): Promise<ArchitectureResponse> {
  const response = await fetchWithTimeout(
    `${API_URL}/api/generate-architecture`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    },
    REQUEST_TIMEOUT_MS
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || 'Failed to generate architecture',
      response.status,
      errorData
    );
  }

  const data = await response.json();

  // Validate response structure at runtime using Zod
  const parseResult = ArchitectureResponseSchema.safeParse(data);
  if (!parseResult.success) {
    console.error('API response validation failed:', parseResult.error);
    throw new ApiError(
      'Invalid response format from server',
      500,
      parseResult.error.issues
    );
  }

  return parseResult.data as ArchitectureResponse;
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetchWithTimeout(
    `${API_URL}/api/health`,
    { method: 'GET' },
    HEALTH_CHECK_TIMEOUT_MS
  );

  if (!response.ok) {
    throw new ApiError('API health check failed', response.status);
  }

  return response.json();
}

/**
 * Stream architecture generation with SSE
 * Calls callbacks as sections arrive
 */
export async function generateArchitectureStreaming(
  request: ArchitectureRequest,
  callbacks: {
    onSection: (section: 'architecture' | 'compliance' | 'deployment', data: Architecture | Compliance | Deployment) => void;
    onError: (error: Error) => void;
    onComplete: () => void;
  }
): Promise<void> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minute timeout

  try {
    const response = await fetch(`${API_URL}/api/generate-architecture-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || 'Streaming request failed',
        response.status,
        errorData
      );
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new ApiError('No response body', 500);
    }

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Parse SSE events from buffer
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const eventData = JSON.parse(line.slice(6));

            if (eventData.section && eventData.data) {
              // Validate each section with appropriate schema
              let validatedData;
              switch (eventData.section) {
                case 'architecture':
                  validatedData = ArchitectureSchema.parse(eventData.data);
                  callbacks.onSection('architecture', validatedData as Architecture);
                  break;
                case 'compliance':
                  validatedData = ComplianceSchema.parse(eventData.data);
                  callbacks.onSection('compliance', validatedData as Compliance);
                  break;
                case 'deployment':
                  validatedData = DeploymentSchema.parse(eventData.data);
                  callbacks.onSection('deployment', validatedData as Deployment);
                  break;
              }
            } else if (eventData.status === 'complete') {
              callbacks.onComplete();
            } else if (eventData.error) {
              callbacks.onError(new Error(eventData.error));
            }
          } catch (parseError) {
            console.error('Error parsing SSE event:', parseError);
          }
        }
      }
    }
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      callbacks.onError(new ApiError('Request timeout', 408));
    } else {
      callbacks.onError(error instanceof Error ? error : new Error('Unknown error'));
    }
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Generate sample code based on architecture context
 */
export async function generateCode(
  request: CodeGenerationRequest
): Promise<SampleCode> {
  const response = await fetchWithTimeout(
    `${API_URL}/api/generate-code`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    },
    60000 // 1 minute timeout for code generation
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || 'Failed to generate code',
      response.status,
      errorData
    );
  }

  const data = await response.json();

  // Validate response structure
  const parseResult = SampleCodeSchema.safeParse(data.sampleCode);
  if (!parseResult.success) {
    console.error('Code response validation failed:', parseResult.error);
    throw new ApiError(
      'Invalid code response format',
      500,
      parseResult.error.issues
    );
  }

  return parseResult.data as SampleCode;
}
