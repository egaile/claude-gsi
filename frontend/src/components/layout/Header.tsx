export function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-anthropic-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">R</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Reference Architecture Generator
            </h1>
            <p className="text-sm text-gray-500">
              Generate healthcare-specific Claude deployment architectures
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
