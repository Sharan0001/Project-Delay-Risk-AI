/**
 * useAnalysis Hook Tests
 * 
 * Tests for the analysis mutation hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useAnalysis } from './useAnalysis';
import * as analysisApi from '../api/analysis';

// Mock the analysis API
vi.mock('../api/analysis', () => ({
    runAnalysis: vi.fn(),
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
    default: {
        success: vi.fn(),
        error: vi.fn(),
    },
}));

// Create wrapper with QueryClient
function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: { retry: false },
            mutations: { retry: false },
        },
    });
    return function Wrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(QueryClientProvider, { client: queryClient }, children);
    };
}

// Mock analysis results
const mockResults = [
    {
        task_id: 'TASK-001',
        risk_level: 'High',
        risk_score: 75,
        delay_probability: 0.82,
        reasons: ['Frequent task blocking'],
        recommended_actions: ['Add resource'],
    },
    {
        task_id: 'TASK-002',
        risk_level: 'Low',
        risk_score: 25,
        delay_probability: 0.15,
        reasons: [],
        recommended_actions: [],
    },
];

describe('useAnalysis', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('starts with empty results and isLoading=false', () => {
        // Act
        const { result } = renderHook(() => useAnalysis(), {
            wrapper: createWrapper(),
        });

        // Assert
        expect(result.current.results).toEqual([]);
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isSuccess).toBe(false);
    });

    it('sets results after successful runAnalysis call', async () => {
        // Arrange
        vi.mocked(analysisApi.runAnalysis).mockResolvedValue({
            results: mockResults,
        });

        // Act
        const { result } = renderHook(() => useAnalysis(), {
            wrapper: createWrapper(),
        });

        // Trigger mutation
        await act(async () => {
            result.current.runAnalysis(null);
        });

        // Wait for mutation to complete
        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        // Assert
        expect(result.current.results).toHaveLength(2);
        expect(result.current.results[0].task_id).toBe('TASK-001');
        expect(result.current.results[0].risk_level).toBe('High');
    });

    it('clears results when clearResults is called', async () => {
        // Arrange
        vi.mocked(analysisApi.runAnalysis).mockResolvedValue({
            results: mockResults,
        });

        const { result } = renderHook(() => useAnalysis(), {
            wrapper: createWrapper(),
        });

        // First, run analysis to populate results
        await act(async () => {
            result.current.runAnalysis(null);
        });

        await waitFor(() => {
            expect(result.current.results).toHaveLength(2);
        });

        // Act - clear results
        act(() => {
            result.current.clearResults();
        });

        // Assert
        expect(result.current.results).toEqual([]);
    });
});
