/**
 * Motion System - Shared Animation Presets
 * 
 * Centralized motion configuration for consistent animations across the app.
 * Design philosophy: subtle, fast, purposeful motion that communicates state.
 * 
 * Rules:
 * - Animate on state change only
 * - Use opacity, transform, or scale only
 * - Duration: 150-250ms
 * - Easing: ease-out for exits, ease-in-out for transitions
 */

import { Variants, Transition } from 'framer-motion';

// ============================================================================
// Core Timing Constants
// ============================================================================

export const DURATION = {
    fast: 0.15,
    normal: 0.2,
    slow: 0.3,
} as const;

export const EASING = {
    easeOut: [0.0, 0.0, 0.2, 1],
    easeInOut: [0.4, 0.0, 0.2, 1],
    spring: { type: 'spring', stiffness: 300, damping: 30 },
} as const;

// ============================================================================
// Transition Presets
// ============================================================================

export const transitions = {
    fast: {
        duration: DURATION.fast,
        ease: EASING.easeOut,
    } as Transition,
    normal: {
        duration: DURATION.normal,
        ease: EASING.easeOut,
    } as Transition,
    slow: {
        duration: DURATION.slow,
        ease: EASING.easeInOut,
    } as Transition,
};

// ============================================================================
// Animation Variants
// ============================================================================

/**
 * Fade in from transparent
 */
export const fadeIn: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: transitions.normal,
    },
};

/**
 * Fade in with slight upward movement
 */
export const slideUp: Variants = {
    hidden: {
        opacity: 0,
        y: 8,
    },
    visible: {
        opacity: 1,
        y: 0,
        transition: transitions.normal,
    },
};

/**
 * Slide in from right (for panels)
 */
export const slideRight: Variants = {
    hidden: {
        opacity: 0,
        x: 24,
    },
    visible: {
        opacity: 1,
        x: 0,
        transition: transitions.slow,
    },
    exit: {
        opacity: 0,
        x: 24,
        transition: transitions.fast,
    },
};

/**
 * Scale in from slightly smaller
 */
export const scaleIn: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.95,
    },
    visible: {
        opacity: 1,
        scale: 1,
        transition: transitions.normal,
    },
};

/**
 * Staggered children animation
 */
export const staggerContainer: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.02,
        },
    },
};

/**
 * Individual stagger item
 */
export const staggerItem: Variants = {
    hidden: { opacity: 0, y: 8 },
    visible: {
        opacity: 1,
        y: 0,
        transition: transitions.normal,
    },
};

// ============================================================================
// Component-Specific Presets
// ============================================================================

/**
 * Stat card entry animation
 */
export const statCardVariants: Variants = {
    hidden: {
        opacity: 0,
        y: 12,
        scale: 0.98,
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            duration: DURATION.normal,
            ease: EASING.easeOut,
        },
    },
};

/**
 * Panel slide-in from right
 */
export const panelVariants: Variants = {
    hidden: {
        opacity: 0,
        x: '100%',
    },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            duration: DURATION.slow,
            ease: EASING.easeOut,
        },
    },
    exit: {
        opacity: 0,
        x: '50%',
        transition: {
            duration: DURATION.fast,
            ease: EASING.easeOut,
        },
    },
};

/**
 * Table row hover animation
 */
export const tableRowVariants: Variants = {
    initial: { backgroundColor: 'transparent' },
    hover: {
        backgroundColor: 'rgba(0, 0, 0, 0.02)',
        transition: transitions.fast,
    },
    focus: {
        backgroundColor: 'rgba(59, 130, 246, 0.05)',
        transition: transitions.fast,
    },
};

/**
 * Progress bar fill animation
 */
export const progressBarVariants: Variants = {
    hidden: { width: 0 },
    visible: (width: number) => ({
        width: `${width}%`,
        transition: {
            duration: DURATION.slow,
            ease: EASING.easeOut,
            delay: 0.1,
        },
    }),
};

/**
 * Collapsible section animation
 */
export const collapseVariants: Variants = {
    hidden: {
        height: 0,
        opacity: 0,
        overflow: 'hidden',
    },
    visible: {
        height: 'auto',
        opacity: 1,
        transition: {
            height: {
                duration: DURATION.normal,
                ease: EASING.easeOut,
            },
            opacity: {
                duration: DURATION.fast,
                delay: 0.05,
            },
        },
    },
};
