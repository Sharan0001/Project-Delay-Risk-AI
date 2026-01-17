/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Dark theme base surfaces (layered depth)
                dark: {
                    bg: '#0B0D0F',       // Deepest background
                    100: '#12151A',      // Primary surface
                    200: '#1A1E24',      // Elevated cards
                    300: '#22272E',      // Hover states
                    400: '#2D333B',      // Borders, dividers
                    500: '#3D444D',      // Subtle elements
                },
                // Light text hierarchy
                light: {
                    100: '#FFFFFF',      // Primary text
                    200: '#E6EDF3',      // Secondary text
                    300: '#9CA3AF',      // Tertiary/muted
                    400: '#6B7280',      // Disabled
                },
                // Risk visualization (vibrant on dark)
                risk: {
                    high: '#F87171',       // Red-400 (softer on dark)
                    'high-bg': 'rgba(248, 113, 113, 0.15)',
                    medium: '#FBBF24',     // Amber-400
                    'medium-bg': 'rgba(251, 191, 36, 0.15)',
                    low: '#34D399',        // Emerald-400
                    'low-bg': 'rgba(52, 211, 153, 0.15)',
                },
                // Primary accent (blue)
                primary: {
                    50: 'rgba(59, 130, 246, 0.1)',
                    100: 'rgba(59, 130, 246, 0.2)',
                    400: '#60A5FA',
                    500: '#3B82F6',
                    600: '#2563EB',
                    700: '#1D4ED8',
                },
                // Legacy surface colors (for gradual migration)
                surface: {
                    50: '#12151A',
                    100: '#1A1E24',
                    200: '#22272E',
                    300: '#3D444D',
                    400: '#6B7280',
                    500: '#9CA3AF',
                    600: '#C9D1DA',
                    700: '#E6EDF3',
                    800: '#F3F4F6',
                    900: '#FFFFFF',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            fontSize: {
                // Refined type scale
                'xs': ['0.75rem', { lineHeight: '1rem' }],
                'sm': ['0.8125rem', { lineHeight: '1.25rem' }],
                'base': ['0.875rem', { lineHeight: '1.5rem' }],
                'lg': ['1rem', { lineHeight: '1.75rem' }],
                'xl': ['1.125rem', { lineHeight: '1.75rem' }],
                '2xl': ['1.25rem', { lineHeight: '2rem' }],
                '3xl': ['1.5rem', { lineHeight: '2rem' }],
                '4xl': ['2rem', { lineHeight: '2.5rem' }],
            },
            boxShadow: {
                'glow-sm': '0 0 15px -3px rgba(59, 130, 246, 0.15)',
                'glow': '0 0 25px -5px rgba(59, 130, 246, 0.2)',
                'card': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2)',
                'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3)',
            },
            borderRadius: {
                'xl': '0.875rem',
                '2xl': '1rem',
            },
            animation: {
                'fade-in': 'fadeIn 0.2s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'slide-in-right': 'slideInRight 0.25s ease-out',
                'pulse-subtle': 'pulseSubtle 2s infinite',
                'glow-pulse': 'glowPulse 2s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideInRight: {
                    '0%': { opacity: '0', transform: 'translateX(20px)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                pulseSubtle: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.7' },
                },
                glowPulse: {
                    '0%, 100%': { boxShadow: '0 0 15px -3px rgba(59, 130, 246, 0.15)' },
                    '50%': { boxShadow: '0 0 25px -5px rgba(59, 130, 246, 0.25)' },
                },
            },
        },
    },
    plugins: [],
}
