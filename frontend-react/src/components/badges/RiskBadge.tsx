/**
 * Risk Badge Component - Dark Theme
 * 
 * Displays risk level with appropriate styling:
 * - Semi-transparent backgrounds
 * - Vibrant text colors
 * - Subtle borders for depth
 */

import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';
import type { RiskLevel } from '../../api';

interface RiskBadgeProps {
    level: RiskLevel;
    showIcon?: boolean;
    size?: 'sm' | 'md';
}

const config: Record<RiskLevel, {
    classes: string;
    icon: typeof AlertTriangle;
}> = {
    High: {
        classes: 'bg-risk-high-bg text-risk-high border-risk-high/25',
        icon: AlertTriangle,
    },
    Medium: {
        classes: 'bg-risk-medium-bg text-risk-medium border-risk-medium/25',
        icon: AlertCircle,
    },
    Low: {
        classes: 'bg-risk-low-bg text-risk-low border-risk-low/25',
        icon: CheckCircle,
    },
};

export function RiskBadge({ level, showIcon = true, size = 'md' }: RiskBadgeProps) {
    const { classes, icon: Icon } = config[level];

    const sizeClasses = size === 'sm'
        ? 'px-2 py-0.5 text-xs gap-1'
        : 'px-2.5 py-1 text-sm gap-1.5';

    const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5';

    return (
        <span
            className={`inline-flex items-center ${classes} ${sizeClasses} rounded-lg font-semibold border`}
            role="status"
            aria-label={`Risk level: ${level}`}
        >
            {showIcon && <Icon className={iconSize} aria-hidden="true" />}
            {level}
        </span>
    );
}
