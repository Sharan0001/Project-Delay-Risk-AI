/**
 * useHealth Hook Tests
 * 
 * Tests for the backend health check hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useHealth } from './useHealth';
import * as api from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
    apiClient: {
        get: vi.fn(),
    },
}));

// Create wrapper with QueryClient
function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: { retry: false, gcTime: 0 },
        },
    });
    return function Wrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(QueryClientProvider, { client: queryClient }, children);
    };
}

describe('useHealth', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('returns connected=true when backend responds with status ok', async () => {
        // Arrange
        vi.mocked(api.apiClient.get).mockResolvedValue({
            data: { status: 'ok', version: '2.1.0' },
        });

        // Act
        const { result } = renderHook(() => useHealth(), {
            wrapper: createWrapper(),
        });

        // Wait for query to complete
        await waitFor(() => {
            expect(result.current.isConnected).toBe(true);
        });

        expect(result.current.version).toBe('2.1.0');
    });

    it('returns version as null initially while loading', () => {
        // Arrange - slow response
        vi.mocked(api.apiClient.get).mockImplementation(
            () => new Promise(() => { }) // Never resolves
        );

        // Act
        const { result } = renderHook(() => useHealth(), {
            wrapper: createWrapper(),
        });

        // Assert - loading state
        expect(result.current.isLoading).toBe(true);
        expect(result.current.version).toBeNull();
    });
});
