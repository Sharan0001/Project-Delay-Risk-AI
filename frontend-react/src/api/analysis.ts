/**
 * Analysis API Service
 * 
 * Provides typed API calls for:
 * - Health check
 * - Running analysis
 * - Fetching history
 * - Getting statistics
 */

import { apiClient } from './client';
import type {
    HealthResponse,
    StatsResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    HistoryResponse,
    AnalysisDetail,
    WhatIfScenario,
} from './types';

/**
 * Checks backend health status
 */
export async function getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
}

/**
 * Gets aggregate statistics from all analyses
 */
export async function getStats(): Promise<StatsResponse> {
    const response = await apiClient.get<StatsResponse>('/stats');
    return response.data;
}

/**
 * Runs a new analysis with optional what-if scenario
 */
export async function runAnalysis(
    whatIf?: WhatIfScenario | null
): Promise<AnalyzeResponse> {
    const request: AnalyzeRequest = {
        what_if: whatIf || null,
    };
    const response = await apiClient.post<AnalyzeResponse>('/analyze', request);
    return response.data;
}

/**
 * Forces a fresh analysis with model retraining
 */
export async function runFreshAnalysis(
    whatIf?: WhatIfScenario | null
): Promise<AnalyzeResponse> {
    const request: AnalyzeRequest = {
        what_if: whatIf || null,
    };
    const response = await apiClient.post<AnalyzeResponse>('/analyze/refresh', request);
    return response.data;
}

/**
 * Gets analysis history
 */
export async function getHistory(limit = 20): Promise<HistoryResponse> {
    const response = await apiClient.get<HistoryResponse>('/history', {
        params: { limit },
    });
    return response.data;
}

/**
 * Gets a specific analysis by ID with full results
 */
export async function getAnalysisById(id: number): Promise<AnalysisDetail> {
    const response = await apiClient.get<AnalysisDetail>(`/history/${id}`);
    return response.data;
}

/**
 * Clears the model cache
 */
export async function clearCache(): Promise<{ status: string }> {
    const response = await apiClient.delete<{ status: string }>('/cache');
    return response.data;
}
