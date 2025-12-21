import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import DOMPurify from 'dompurify';
import { cn } from '../../lib/utils';

// Initialize mermaid once at module level
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'strict', // Prevent XSS attacks through diagram content
  fontFamily: 'Inter, system-ui, sans-serif',
});

interface MermaidDiagramProps {
  diagram: string;
  className?: string;
}

export function MermaidDiagram({ diagram, className }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!diagram) return;

      try {
        // Generate unique ID for this render
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        const { svg: renderedSvg } = await mermaid.render(id, diagram);
        // Sanitize SVG to prevent XSS attacks (defense in depth)
        // Allow foreignObject and related elements needed for Mermaid text labels
        const sanitizedSvg = DOMPurify.sanitize(renderedSvg, {
          USE_PROFILES: { svg: true, svgFilters: true },
          ADD_TAGS: ['foreignObject', 'use'],
          ADD_ATTR: ['dominant-baseline', 'xlink:href', 'requiredExtensions'],
        });
        setSvg(sanitizedSvg);
        setError(null);
      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setError(err instanceof Error ? err.message : 'Failed to render diagram');
        setSvg('');
      }
    };

    renderDiagram();
  }, [diagram]);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-medium">Diagram Rendering Error</p>
        <p className="text-red-600 text-sm mt-1">{error}</p>
        <details className="mt-3">
          <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
            View raw diagram code
          </summary>
          <pre className="mt-2 text-xs bg-gray-900 text-gray-100 p-3 rounded overflow-auto max-h-64">
            {diagram}
          </pre>
        </details>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="flex items-center justify-center h-48 bg-gray-50 rounded-lg">
        <div className="animate-pulse text-gray-400">Loading diagram...</div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn('mermaid overflow-x-auto', className)}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

// Export function to get raw SVG for export
export function getSvgFromDiagram(diagram: string): Promise<string> {
  const id = `mermaid-export-${Date.now()}`;
  return mermaid.render(id, diagram).then(({ svg }) => svg);
}
