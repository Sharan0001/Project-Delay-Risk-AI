/**
 * Application Configuration
 * 
 * Centralized config for app metadata, feature flags, and environment settings.
 * All hardcoded values should live here for easy maintenance.
 */

// App version - update this when releasing new versions
export const APP_VERSION = '2.1.0';

// App metadata
export const APP_CONFIG = {
    name: 'Project Risk AI',
    fullName: 'Project Delay Risk AI',
    description: 'Decision Intelligence System',
    version: APP_VERSION,

    // Links
    githubUrl: 'https://github.com',
    documentationUrl: '#',

    // API configuration
    api: {
        baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
        timeout: 30000,
        retryAttempts: 2,
    },

    // Feature flags
    features: {
        darkMode: false,  // Not yet implemented
        exportPdf: false, // Not yet implemented
        exportCsv: false, // Not yet implemented
    },

    // UI defaults
    defaults: {
        analysisLimit: 20,
        historyLimit: 20,
        pollingInterval: 30000, // 30 seconds
        toastDuration: 4000,
    },

    // Risk thresholds (matches backend)
    riskThresholds: {
        high: 60,
        medium: 40,
    },
} as const;

// Environment helpers
export const ENV = {
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
    mode: import.meta.env.MODE,
} as const;

// Type exports
export type AppConfig = typeof APP_CONFIG;
export type Environment = typeof ENV;
