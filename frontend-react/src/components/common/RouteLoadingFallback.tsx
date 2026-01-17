/**
 * Route Loading Indicator - Dark Theme
 * 
 * Full-screen loading state for route transitions.
 * Uses subtle pulse animation to indicate activity.
 */

import { Brain } from 'lucide-react';

export function RouteLoadingFallback() {
    return (
        <div className="animate-fade-in flex flex-col items-center justify-center py-24">
            <div className="w-14 h-14 bg-primary-500/15 rounded-xl flex items-center justify-center mb-4 animate-pulse-subtle">
                <Brain className="w-7 h-7 text-primary-400" />
            </div>
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <p className="text-sm text-light-400 mt-4">Loading...</p>
        </div>
    );
}
