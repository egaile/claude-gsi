import type { ArchitectureRequest, ArchitectureResponse } from './types';

const API_URL = import.meta.env.VITE_API_URL || '';

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

export async function generateArchitecture(
  request: ArchitectureRequest
): Promise<ArchitectureResponse> {
  const response = await fetch(`${API_URL}/api/generate-architecture`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || 'Failed to generate architecture',
      response.status,
      errorData
    );
  }

  return response.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/api/health`);
  
  if (!response.ok) {
    throw new ApiError('API health check failed', response.status);
  }
  
  return response.json();
}
