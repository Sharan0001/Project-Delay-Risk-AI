/**
 * Axios HTTP Client Configuration
 * 
 * Centralizes API configuration including:
 * - Base URL from environment or default
 * - Request/response interceptors
 * - Error handling
 * - API key authentication
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import toast from 'react-hot-toast';

// Environment configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

/**
 * Creates and configures the Axios instance
 */
function createApiClient(): AxiosInstance {
    const client = axios.create({
        baseURL: API_BASE_URL,
        timeout: 60000, // 60 seconds for analysis operations
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Request interceptor: Add API key if configured
    client.interceptors.request.use(
        (config) => {
            if (API_KEY) {
                config.headers['x-api-key'] = API_KEY;
            }
            return config;
        },
        (error) => Promise.reject(error)
    );

    // Response interceptor: Handle common errors
    client.interceptors.response.use(
        (response) => response,
        (error: AxiosError) => {
            // Extract error message
            const message = extractErrorMessage(error);

            // Handle specific status codes
            switch (error.response?.status) {
                case 401:
                    toast.error('Authentication failed. Check your API key.');
                    break;
                case 429:
                    toast.error('Rate limit exceeded. Please wait before trying again.');
                    break;
                case 500:
                    toast.error('Server error. Please try again later.');
                    break;
                case undefined:
                    toast.error('Unable to connect to server. Is the backend running?');
                    break;
                default:
                    toast.error(message);
            }

            return Promise.reject(error);
        }
    );

    return client;
}

/**
 * Extracts a user-friendly error message from an Axios error
 */
function extractErrorMessage(error: AxiosError): string {
    if (error.response?.data) {
        const data = error.response.data as Record<string, unknown>;
        if (typeof data.detail === 'string') {
            return data.detail;
        }
        if (typeof data.message === 'string') {
            return data.message;
        }
    }
    return error.message || 'An unexpected error occurred';
}

// Export singleton instance
export const apiClient = createApiClient();

// Export for testing/mocking purposes
export { API_BASE_URL, API_KEY };
