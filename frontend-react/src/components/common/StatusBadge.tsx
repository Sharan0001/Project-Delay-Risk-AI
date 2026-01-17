/**
 * Enhanced Status Badge Component - Dark Theme
 * 
 * Displays connection status with:
 * - Animated pulse indicator for connected state
 * - Clear visual states (loading, connected, disconnected)
 * - Hover tooltip with backend info
 */

import { XCircle, Loader2, Server } from 'lucide-react';

interface StatusBadgeProps {
    isConnected: boolean;
    isLoading: boolean;
    version?: string | null;
}

export function StatusBadge({ isConnected, isLoading, version }: StatusBadgeProps) {
    if (isLoading) {
        return (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-300 rounded-lg">
                <Loader2 className="w-4 h-4 text-primary-400 animate-spin" />
                <span className="text-sm text-light-300">Connecting...</span>
            </div>
        );
    }

    if (isConnected) {
        return (
            <div className="group relative flex items-center gap-2 px-3 py-1.5 bg-risk-low/15 border border-risk-low/20 rounded-lg cursor-default">
                {/* Animated pulse dot */}
                <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-risk-low opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-risk-low"></span>
                </span>

                <span className="text-sm text-risk-low font-medium">Connected</span>
                {version && (
                    <span className="text-xs text-light-400 font-mono">v{version}</span>
                )}

                {/* Hover tooltip */}
                <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-dark-300 border border-dark-400 text-light-100 text-xs rounded-lg shadow-lg z-[100] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                    <div className="flex items-center gap-2">
                        <Server className="w-3 h-3" />
                        <span>Backend API Running</span>
                    </div>
                    {version && <div className="mt-1 text-light-400">Version {version}</div>}
                    <div className="absolute top-full right-4 border-4 border-transparent border-t-dark-300" />
                </div>
            </div>
        );
    }

    return (
        <div className="group relative flex items-center gap-2 px-3 py-1.5 bg-risk-high/15 border border-risk-high/20 rounded-lg cursor-default">
            <XCircle className="w-4 h-4 text-risk-high" />
            <span className="text-sm text-risk-high font-medium">Disconnected</span>

            {/* Hover tooltip */}
            <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-dark-300 border border-dark-400 text-light-100 text-xs rounded-lg shadow-lg z-[100] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                <div className="flex items-center gap-2 text-risk-high">
                    <XCircle className="w-3 h-3" />
                    <span>Backend Not Responding</span>
                </div>
                <div className="mt-1 text-light-400">Start the server to continue</div>
                <div className="absolute top-full right-4 border-4 border-transparent border-t-dark-300" />
            </div>
        </div>
    );
}
