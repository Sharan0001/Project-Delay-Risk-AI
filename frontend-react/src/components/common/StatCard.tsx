/**
 * Stat Card Component - Dark Theme
 * 
 * Modern metric card with:
 * - Dark layered surface
 * - Animated entry
 * - Animated number transitions
 * - Hover glow effect
 * - Tooltip on hover
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, Info } from 'lucide-react';
import { useAnimatedCounter } from '../../hooks';
import { statCardVariants, fadeIn } from '../../lib/motion';

interface StatCardProps {
    label: string;
    value: string | number;
    icon?: LucideIcon;
    iconColor?: string;
    iconBg?: string;
    tooltip?: string;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    isLoading?: boolean;
    index?: number;
}

export function StatCard({
    label,
    value,
    icon: Icon,
    iconColor = 'text-primary-400',
    iconBg = 'bg-primary-500/10',
    tooltip,
    trend,
    isLoading = false,
    index = 0,
}: StatCardProps) {
    const [showTooltip, setShowTooltip] = useState(false);

    // Animate numeric values
    const numericValue = typeof value === 'number' ? value : null;
    const animatedValue = useAnimatedCounter(numericValue ?? 0);

    // Format display value
    const displayValue = numericValue !== null
        ? formatStatValue(animatedValue)
        : value;

    if (isLoading) {
        return (
            <div className="stat-card">
                <div className="flex items-center justify-between mb-4">
                    <div className="skeleton h-4 w-24" />
                    <div className="skeleton h-10 w-10 rounded-lg" />
                </div>
                <div className="skeleton h-9 w-28" />
            </div>
        );
    }

    return (
        <motion.div
            className="stat-card group"
            variants={statCardVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: index * 0.05 }}
            onMouseEnter={() => tooltip && setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
        >
            {/* Tooltip */}
            {tooltip && showTooltip && (
                <motion.div
                    className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-3 py-2 
                               bg-dark-300 border border-dark-400 text-light-200 text-xs 
                               rounded-lg shadow-lg z-50 max-w-xs text-center"
                    variants={fadeIn}
                    initial="hidden"
                    animate="visible"
                >
                    {tooltip}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 
                                    border-[6px] border-transparent border-t-dark-300" />
                </motion.div>
            )}

            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className="text-sm text-light-300 font-medium">{label}</span>
                    {tooltip && (
                        <Info className="w-3.5 h-3.5 text-light-400 group-hover:text-light-300 transition-colors" />
                    )}
                </div>
                {Icon && (
                    <div className={`p-2.5 rounded-lg ${iconBg}`}>
                        <Icon className={`w-5 h-5 ${iconColor}`} />
                    </div>
                )}
            </div>

            {/* Value */}
            <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold text-light-100 tabular-nums tracking-tight">
                    {displayValue}
                </span>

                {trend && (
                    <motion.span
                        className={`text-xs font-semibold px-2 py-1 rounded-md ${trend.isPositive
                            ? 'text-risk-low bg-risk-low-bg'
                            : 'text-risk-high bg-risk-high-bg'
                            }`}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.2, duration: 0.15 }}
                    >
                        {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                    </motion.span>
                )}
            </div>
        </motion.div>
    );
}

/**
 * Format stat values with appropriate precision
 */
function formatStatValue(value: number): string {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    }
    if (value >= 10000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    if (Number.isInteger(value)) {
        return value.toLocaleString();
    }
    return value.toFixed(1);
}
