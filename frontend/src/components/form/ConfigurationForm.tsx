import type { ArchitectureRequest } from '../../lib/types';
import {
  USE_CASE_OPTIONS,
  CLOUD_PLATFORM_OPTIONS,
  INTEGRATION_PATTERN_OPTIONS,
  DATA_CLASSIFICATION_OPTIONS,
  SCALE_TIER_OPTIONS,
} from '../../lib/types';

interface ConfigurationFormProps {
  formData: ArchitectureRequest;
  setFormData: React.Dispatch<React.SetStateAction<ArchitectureRequest>>;
  onGenerate: () => void;
  isLoading: boolean;
}

export function ConfigurationForm({
  formData,
  setFormData,
  onGenerate,
  isLoading,
}: ConfigurationFormProps) {
  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Configure Your Architecture
      </h2>

      <div className="space-y-6">
        {/* Use Case Select */}
        <div>
          <label className="label">Use Case</label>
          <select
            className="select mt-1"
            value={formData.useCase}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                useCase: e.target.value as ArchitectureRequest['useCase'],
              }))
            }
          >
            {Object.entries(USE_CASE_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {USE_CASE_OPTIONS[formData.useCase].description}
          </p>
        </div>

        {/* Cloud Platform Select */}
        <div>
          <label className="label">Cloud Platform</label>
          <select
            className="select mt-1"
            value={formData.cloudPlatform}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                cloudPlatform: e.target.value as ArchitectureRequest['cloudPlatform'],
              }))
            }
          >
            {Object.entries(CLOUD_PLATFORM_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {CLOUD_PLATFORM_OPTIONS[formData.cloudPlatform].description}
          </p>
        </div>

        {/* Integration Pattern Select */}
        <div>
          <label className="label">Integration Pattern</label>
          <select
            className="select mt-1"
            value={formData.integrationPattern}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                integrationPattern: e.target.value as ArchitectureRequest['integrationPattern'],
              }))
            }
          >
            {Object.entries(INTEGRATION_PATTERN_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {INTEGRATION_PATTERN_OPTIONS[formData.integrationPattern].description}
          </p>
        </div>

        {/* Data Classification Select */}
        <div>
          <label className="label">Data Classification</label>
          <select
            className="select mt-1"
            value={formData.dataClassification}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                dataClassification: e.target.value as ArchitectureRequest['dataClassification'],
              }))
            }
          >
            {Object.entries(DATA_CLASSIFICATION_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {DATA_CLASSIFICATION_OPTIONS[formData.dataClassification].description}
          </p>
        </div>

        {/* Scale Tier Select */}
        <div>
          <label className="label">Scale Tier</label>
          <select
            className="select mt-1"
            value={formData.scaleTier}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                scaleTier: e.target.value as ArchitectureRequest['scaleTier'],
              }))
            }
          >
            {Object.entries(SCALE_TIER_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {SCALE_TIER_OPTIONS[formData.scaleTier].description}
          </p>
        </div>

        {/* Generate Button */}
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="btn-primary w-full"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating Architecture...
            </span>
          ) : (
            'Generate Architecture'
          )}
        </button>
      </div>
    </div>
  );
}
