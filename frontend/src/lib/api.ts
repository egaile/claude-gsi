import type { ArchitectureRequest, ArchitectureResponse } from './types';
import { ArchitectureResponseSchema } from './schema';

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
