/**
 * Error Fallback Component - Dark Theme
 * 
 * Displayed when an unhandled error occurs in the React tree.
 * Provides:
 * - Error ID for support tickets
 * - Technical details (in dev mode)
 * - Retry and reload options
 * - Professional, calming design
 */

import { AlertOctagon, RefreshCw, Home } from 'lucide-react';
import type { FallbackProps } from 'react-error-boundary';

/**
 * Generates a short error ID for tracking
 */
function generateErrorId(): string {
    return `ERR-${Date.now().toString(36).toUpperCase().slice(-6)}`;
}

export function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
    const errorId = generateErrorId();
    const isDev = import.meta.env.DEV;

    return (
        <div className="min-h-screen bg-dark-bg flex items-center justify-center p-8">
            <div className="max-w-lg w-full">
                {/* Error Icon */}
                <div className="flex justify-center mb-6">
                    <div className="w-16 h-16 bg-risk-high/15 rounded-2xl flex items-center justify-center">
                        <AlertOctagon className="w-8 h-8 text-risk-high" />
                    </div>
                </div>

                {/* Heading */}
                <h1 className="text-xl font-semibold text-light-100 text-center mb-2">
                    Something went wrong
                </h1>
                <p className="text-light-300 text-center mb-6">
                    An unexpected error occurred. The issue has been logged.
                </p>

                {/* Error ID Card */}
                <div className="bg-dark-200 border border-dark-400/50 rounded-xl p-4 mb-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-light-400 uppercase tracking-wider">
                            Error Reference
                        </span>
                        <span className="font-mono text-sm font-medium text-light-100">
                            {errorId}
                        </span>
                    </div>

                    {/* Show error details in dev mode */}
                    {isDev && (
                        <div className="mt-3 pt-3 border-t border-dark-400/50">
                            <span className="text-xs font-medium text-light-400 uppercase tracking-wider block mb-2">
                                Error Details (Dev Only)
                            </span>
                            <pre className="text-xs text-risk-high font-mono bg-dark-300 p-3 rounded-lg border border-dark-400/50 overflow-x-auto max-h-32">
                                {error.message}
                                {error.stack && (
                                    <>
                                        {'\n\n'}
                                        {error.stack.split('\n').slice(1, 5).join('\n')}
                                    </>
                                )}
                            </pre>
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                    <button
                        onClick={resetErrorBoundary}
                        className="flex-1 btn-primary flex items-center justify-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Try Again
                    </button>
                    <button
                        onClick={() => window.location.href = '/'}
                        className="flex-1 btn-secondary flex items-center justify-center gap-2"
                    >
                        <Home className="w-4 h-4" />
                        Go Home
                    </button>
                </div>

                {/* Footer */}
                <p className="text-xs text-light-400 text-center mt-6">
                    If this keeps happening, please contact support with the error reference.
                </p>
            </div>
        </div>
    );
}
