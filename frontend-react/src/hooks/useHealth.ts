/**
 * Health Check Hook
 * 
 * Provides reactive backend health status with:
 * - Auto-polling every 30 seconds
 * - Connection state tracking
 * - Version information
 */

import { useQuery } from '@tanstack/react-query';
import { getHealth } from '../api';

export interface HealthState {
    isConnected: boolean;
    version: string | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
}

/**
 * Hook for monitoring backend health
 */
export function useHealth(): HealthState {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ['health'],
        queryFn: getHealth,
        refetchInterval: 30000, // Poll every 30 seconds
        retry: 2,
        staleTime: 10000,
    });

    return {
        isConnected: !!data && data.status === 'ok',
        version: data?.version ?? null,
        isLoading,
        error: error as Error | null,
        refetch,
    };
}
