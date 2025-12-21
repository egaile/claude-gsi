import { useState } from 'react';
import type { ArchitectureRequest, GenerationState } from './lib/types';
import { generateArchitecture } from './lib/api';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { ConfigurationForm } from './components/form/ConfigurationForm';
import { InfoPanel } from './components/form/InfoPanel';
import { ResultsDashboard } from './components/results/ResultsDashboard';

function App() {
  const [state, setState] = useState<GenerationState>({ status: 'idle' });
  const [formData, setFormData] = useState<ArchitectureRequest>({
    useCase: 'clinical-documentation',
    cloudPlatform: 'aws-bedrock',
    integrationPattern: 'api-gateway',
    dataClassification: 'phi',
    scaleTier: 'production',
  });

  const handleGenerate = async () => {
    setState({ status: 'loading' });

    try {
      const response = await generateArchitecture(formData);
      setState({ status: 'success', response });
    } catch (error) {
      setState({
        status: 'error',
        error: error instanceof Error ? error.message : 'An error occurred',
      });
    }
  };

  const handleReset = () => {
    setState({ status: 'idle' });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 w-full">
        {state.status === 'idle' || state.status === 'loading' ? (
          <div className="grid lg:grid-cols-2 gap-8">
            <ConfigurationForm
              formData={formData}
              setFormData={setFormData}
              onGenerate={handleGenerate}
              isLoading={state.status === 'loading'}
            />
            <InfoPanel />
          </div>
        ) : state.status === 'success' && state.response ? (
          <ResultsDashboard response={state.response} request={formData} onReset={handleReset} />
        ) : (
          <div className="card p-6 border-red-200 bg-red-50">
            <h2 className="text-lg font-semibold text-red-900 mb-2">
              Generation Failed
            </h2>
            <p className="text-red-700 mb-4">{state.error}</p>
            <button onClick={handleReset} className="btn-secondary">
              Try Again
            </button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
