/**
 * Analysis Hook
 * 
 * Provides complete analysis functionality:
 * - Run new analysis
 * - Get current results
 * - Load from history
 * - Loading and error states
 * - Statistics
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { runAnalysis, getStats } from '../api';
import type { WhatIfScenario, TaskRiskResult, StatsResponse } from '../api';
import toast from 'react-hot-toast';

// Shared query key for analysis results - MUST be same across all usages
const ANALYSIS_RESULTS_KEY = ['analysis', 'current-results'];

/**
 * Hook for fetching aggregate statistics
 */
export function useStats() {
    return useQuery<StatsResponse>({
        queryKey: ['stats'],
        queryFn: getStats,
        staleTime: 60000, // 1 minute
    });
}

/**
 * Hook for running analysis with mutation
 * Results are stored in React Query cache so they persist across page navigations
 */
export function useAnalysis() {
    const queryClient = useQueryClient();

    // Get results from React Query cache (persists across navigations)
    const { data: cachedResults } = useQuery<TaskRiskResult[]>({
        queryKey: ANALYSIS_RESULTS_KEY,
        queryFn: () => [], // Default to empty array
        staleTime: Infinity, // Never auto-refetch
        gcTime: Infinity, // Never garbage collect
    });

    const results = cachedResults ?? [];

    const mutation = useMutation({
        mutationFn: (scenario?: WhatIfScenario | null) => {
            return runAnalysis(scenario);
        },
        onSuccess: (data, scenario) => {
            // Store results in React Query cache (persists across navigations)
            queryClient.setQueryData(ANALYSIS_RESULTS_KEY, data.results);

            // Invalidate stats and history to refresh
            queryClient.invalidateQueries({ queryKey: ['stats'] });
            queryClient.invalidateQueries({ queryKey: ['history'] });

            const scenarioLabel = scenario
                ? ` with "${scenario.replace('_', ' ')}" scenario`
                : '';
            toast.success(`Analysis complete!${scenarioLabel} ${data.results.length} tasks analyzed.`);
        },
        onError: () => {
            // Error toast handled by axios interceptor
        },
    });

    return {
        runAnalysis: mutation.mutate,
        results,
        isLoading: mutation.isPending,
        error: mutation.error as Error | null,
        isSuccess: mutation.isSuccess || results.length > 0,
        clearResults: () => {
            queryClient.setQueryData(ANALYSIS_RESULTS_KEY, []);
        },
    };
}

/**
 * Hook to get cached analysis results (deprecated - use useAnalysis instead)
 */
export function useAnalysisResults() {
    const queryClient = useQueryClient();
    return queryClient.getQueryData<TaskRiskResult[]>(['analysis', 'latest']) ?? [];
}

// Export the key for use in useHistory
export { ANALYSIS_RESULTS_KEY };
