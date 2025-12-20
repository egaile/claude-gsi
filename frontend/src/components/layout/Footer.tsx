export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-500">
            Built by Ed Gaile - Portfolio Project for Anthropic PSA Role
          </p>
          <div className="flex gap-4 text-sm">
            <a
              href="https://github.com/egaile"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-anthropic-600 transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://linkedin.com/in/edgaile"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-anthropic-600 transition-colors"
            >
              LinkedIn
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
