/**
 * Animated Counter Hook
 * 
 * Provides smooth number transitions for statistics.
 * Creates a "counting up" effect when values change.
 */

import { useState, useEffect, useRef } from 'react';

interface UseAnimatedCounterOptions {
    duration?: number;  // Animation duration in ms
    easing?: (t: number) => number;  // Easing function
}

/**
 * Hook that animates a number from its previous value to the current value
 */
export function useAnimatedCounter(
    targetValue: number,
    options: UseAnimatedCounterOptions = {}
): number {
    const { duration = 500, easing = easeOutQuart } = options;

    const [displayValue, setDisplayValue] = useState(targetValue);
    const previousValue = useRef(targetValue);
    const animationRef = useRef<number | null>(null);
    const startTimeRef = useRef<number | null>(null);

    useEffect(() => {
        // If target hasn't changed, no animation needed
        if (targetValue === previousValue.current) return;

        const startValue = previousValue.current;
        const difference = targetValue - startValue;

        // Clean up any existing animation
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
        }

        const animate = (currentTime: number) => {
            if (!startTimeRef.current) {
                startTimeRef.current = currentTime;
            }

            const elapsed = currentTime - startTimeRef.current;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easing(progress);

            const currentValue = startValue + (difference * easedProgress);
            setDisplayValue(Math.round(currentValue * 10) / 10);

            if (progress < 1) {
                animationRef.current = requestAnimationFrame(animate);
            } else {
                setDisplayValue(targetValue);
                previousValue.current = targetValue;
                startTimeRef.current = null;
            }
        };

        animationRef.current = requestAnimationFrame(animate);

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [targetValue, duration, easing]);

    // Update previousValue when animation completes or on initial render
    useEffect(() => {
        previousValue.current = targetValue;
    }, []);

    return displayValue;
}

/**
 * Easing function: easeOutQuart
 * Fast start, slow finish - feels responsive
 */
function easeOutQuart(t: number): number {
    return 1 - Math.pow(1 - t, 4);
}

/**
 * Format large numbers with K/M suffix
 */
export function formatNumber(value: number): string {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    }
    if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    return value.toString();
}
