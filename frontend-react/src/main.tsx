import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import { Toaster } from 'react-hot-toast'
import App from './App'
import { ErrorFallback } from './components/common'
import './index.css'

// Configure React Query client with sensible defaults
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Stale time: 30 seconds before considering data stale
            staleTime: 30 * 1000,
            // Cache time: 5 minutes
            gcTime: 5 * 60 * 1000,
            // Retry failed requests once
            retry: 1,
            // Refetch on window focus (useful for real-time data)
            refetchOnWindowFocus: true,
        },
    },
})

/**
 * Error boundary reset handler
 * Clears React Query cache to ensure fresh state after error recovery
 */
function handleErrorReset() {
    queryClient.clear();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ErrorBoundary
            FallbackComponent={ErrorFallback}
            onReset={handleErrorReset}
        >
            <QueryClientProvider client={queryClient}>
                <BrowserRouter>
                    <App />
                    <Toaster
                        position="top-right"
                        toastOptions={{
                            duration: 4000,
                            style: {
                                background: '#1E293B',
                                color: '#F8FAFC',
                            },
                        }}
                    />
                </BrowserRouter>
            </QueryClientProvider>
        </ErrorBoundary>
    </React.StrictMode>,
)

