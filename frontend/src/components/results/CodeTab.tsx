import { useState } from 'react';
import { Download, Code } from 'lucide-react';
import { CopyButton } from '../ui/CopyButton';
import { cn, downloadFile } from '../../lib/utils';
import type { SampleCode } from '../../lib/types';

interface CodeTabProps {
  sampleCode?: SampleCode;
  onGenerateCode?: () => void;
  isLoading?: boolean;
}

type Language = 'python' | 'typescript';

const LANGUAGES: { id: Language; label: string; extension: string; mimeType: string }[] = [
  { id: 'python', label: 'Python', extension: 'py', mimeType: 'text/x-python' },
  { id: 'typescript', label: 'TypeScript', extension: 'ts', mimeType: 'text/typescript' },
];

export function CodeTab({ sampleCode, onGenerateCode, isLoading }: CodeTabProps) {
  const [activeLanguage, setActiveLanguage] = useState<Language>('python');

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-anthropic-600 mb-4"></div>
        <p className="text-gray-600 font-medium">Generating sample code...</p>
        <p className="text-gray-500 text-sm mt-1">This typically takes 30-45 seconds</p>
      </div>
    );
  }

  // Show generate button if no code
  if (!sampleCode) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Code className="w-16 h-16 text-gray-300 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Sample Code Available on Demand
        </h3>
        <p className="text-gray-600 max-w-md mb-6">
          Generate production-quality Python and TypeScript integration code tailored to your architecture configuration.
        </p>
        {onGenerateCode && (
          <button
            onClick={onGenerateCode}
            className="btn-primary flex items-center gap-2"
          >
            <Code className="w-5 h-5" />
            Generate Sample Code
          </button>
        )}
      </div>
    );
  }

  const handleDownload = () => {
    const lang = LANGUAGES.find((l) => l.id === activeLanguage)!;
    const code = sampleCode[activeLanguage];
    downloadFile(code, `claude-integration.${lang.extension}`, lang.mimeType);
  };

  const currentCode = sampleCode[activeLanguage];

  return (
    <div className="space-y-4">
      {/* Language Toggle + Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex gap-2">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.id}
              onClick={() => setActiveLanguage(lang.id)}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm transition-colors',
                activeLanguage === lang.id
                  ? 'bg-anthropic-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {lang.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <CopyButton text={currentCode} label="Copy" />
          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            <Download className="w-4 h-4" />
            Download
          </button>
        </div>
      </div>

      {/* Code Display */}
      <div className="card overflow-hidden p-0">
        <pre className="!rounded-xl !m-0 max-h-[600px] overflow-auto">
          <code>{currentCode}</code>
        </pre>
      </div>
    </div>
  );
}
