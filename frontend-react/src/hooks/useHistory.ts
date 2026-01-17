/**
 * History Hook
 * 
 * Provides analysis history functionality:
 * - Fetch past analyses
 * - Load specific analysis by ID
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getHistory, getAnalysisById } from '../api';
import type { AnalysisDetail } from '../api';
import toast from 'react-hot-toast';
import { ANALYSIS_RESULTS_KEY } from './useAnalysis';

/**
 * Hook for fetching analysis history
 */
export function useHistory(limit = 20) {
    return useQuery({
        queryKey: ['history', limit],
        queryFn: () => getHistory(limit),
        staleTime: 30000, // 30 seconds
    });
}

/**
 * Hook for loading a specific analysis by ID
 * Stores results in shared cache so Analysis page can pick them up
 */
export function useLoadAnalysis() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => getAnalysisById(id),
        onSuccess: (data: AnalysisDetail) => {
            // Store results in shared cache for Analysis page to pick up
            if (data.results && data.results.length > 0) {
                queryClient.setQueryData(ANALYSIS_RESULTS_KEY, data.results);
            }
            toast.success(`Loaded analysis #${data.id} with ${data.results?.length ?? 0} tasks`);
        },
        onError: () => {
            // Error handled by axios interceptor
        },
    });
}
