import { useState, useCallback } from 'react';
import type {
  ArchitectureRequest,
  StreamingState,
  Architecture,
  Compliance,
  Deployment
} from './lib/types';
import { generateArchitectureStreaming, generateCode } from './lib/api';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { ConfigurationForm } from './components/form/ConfigurationForm';
import { InfoPanel } from './components/form/InfoPanel';
import { ResultsDashboard } from './components/results/ResultsDashboard';

function App() {
  const [state, setState] = useState<StreamingState>({ status: 'idle' });
  const [formData, setFormData] = useState<ArchitectureRequest>({
    useCase: 'clinical-documentation',
    cloudPlatform: 'aws-bedrock',
    integrationPattern: 'api-gateway',
    dataClassification: 'phi',
    scaleTier: 'production',
  });

  const handleGenerate = useCallback(async () => {
    setState({ status: 'streaming' });

    await generateArchitectureStreaming(formData, {
      onSection: (section, data) => {
        setState((prev) => ({
          ...prev,
          [section]: data as Architecture | Compliance | Deployment,
        }));
      },
      onError: (error) => {
        setState((prev) => ({
          ...prev,
          status: 'error',
          error: error.message,
        }));
      },
      onComplete: () => {
        setState((prev) => ({
          ...prev,
          status: 'success',
        }));
      },
    });
  }, [formData]);

  const handleGenerateCode = useCallback(async () => {
    if (!state.architecture) return;

    setState((prev) => ({ ...prev, codeLoading: true }));

    try {
      // Create a summary of the architecture for code generation context
      const architectureSummary = `Components: ${state.architecture.components
        .map((c) => `${c.name} (${c.service})`)
        .join(', ')}. PHI touchpoints: ${state.architecture.components
        .filter((c) => c.phiTouchpoint)
        .map((c) => c.service)
        .join(', ')}.`;

      const sampleCode = await generateCode({
        useCase: formData.useCase,
        cloudPlatform: formData.cloudPlatform,
        architectureSummary,
      });

      setState((prev) => ({
        ...prev,
        sampleCode,
        codeLoading: false,
      }));
    } catch (error) {
      console.error('Code generation failed:', error);
      setState((prev) => ({
        ...prev,
        codeLoading: false,
      }));
    }
  }, [state.architecture, formData.useCase, formData.cloudPlatform]);

  const handleReset = () => {
    setState({ status: 'idle' });
  };

  // Determine if we should show results (streaming or success with at least architecture)
  const showResults =
    (state.status === 'streaming' || state.status === 'success') &&
    state.architecture;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 w-full">
        {state.status === 'idle' || (state.status === 'streaming' && !state.architecture) ? (
          <div className="grid lg:grid-cols-2 gap-8">
            <ConfigurationForm
              formData={formData}
              setFormData={setFormData}
              onGenerate={handleGenerate}
              isLoading={state.status === 'streaming'}
            />
            <InfoPanel />
          </div>
        ) : showResults ? (
          <ResultsDashboard
            architecture={state.architecture}
            compliance={state.compliance}
            deployment={state.deployment}
            sampleCode={state.sampleCode}
            request={formData}
            onReset={handleReset}
            onGenerateCode={handleGenerateCode}
            codeLoading={state.codeLoading}
            isStreaming={state.status === 'streaming'}
          />
        ) : state.status === 'error' ? (
          <div className="card p-6 border-red-200 bg-red-50">
            <h2 className="text-lg font-semibold text-red-900 mb-2">
              Generation Failed
            </h2>
            <p className="text-red-700 mb-4">{state.error}</p>
            <button onClick={handleReset} className="btn-secondary">
              Try Again
            </button>
          </div>
        ) : null}
      </main>

      <Footer />
    </div>
  );
}

export default App;
