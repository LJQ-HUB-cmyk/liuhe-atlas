import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error boundary — catches render-time errors and shows a graceful fallback
 * instead of letting the whole app go black.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Atlas UI error:', error, info);
  }

  reset = () => this.setState({ hasError: false, error: null });

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error!, this.reset);
      }
      return (
        <div className="min-h-screen bg-bg-base text-ink-primary flex items-center justify-center p-8">
          <div className="panel p-6 max-w-md">
            <div className="text-red-400 text-sm font-semibold mb-2">
              ⚠ Something went wrong
            </div>
            <div className="text-ink-secondary text-xs font-mono mb-4 leading-relaxed">
              {this.state.error?.message}
            </div>
            <button
              type="button"
              onClick={this.reset}
              className="px-3 py-1.5 rounded text-xs bg-emerald-500/15 border border-emerald-500/40 text-emerald-200"
            >
              Reset
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}