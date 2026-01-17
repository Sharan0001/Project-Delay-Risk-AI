/**
 * Enhanced Risk Filter Component - Dark Theme
 * 
 * Filter tabs for selecting risk levels with:
 * - Color-coded dot indicators
 * - Animated selection state
 * - Clear visual hierarchy
 */

import type { RiskLevel } from '../../api';

export type FilterValue = 'all' | RiskLevel;

interface RiskFilterProps {
    value: FilterValue;
    onChange: (value: FilterValue) => void;
    counts: {
        all: number;
        high: number;
        medium: number;
        low: number;
    };
}

const FILTERS: {
    value: FilterValue;
    label: string;
    dotColor: string;
    activeColor: string;
    activeBg: string;
}[] = [
        {
            value: 'all',
            label: 'All',
            dotColor: 'bg-light-400',
            activeColor: 'text-light-100',
            activeBg: 'bg-dark-400',
        },
        {
            value: 'High',
            label: 'High',
            dotColor: 'bg-risk-high',
            activeColor: 'text-risk-high',
            activeBg: 'bg-risk-high-bg',
        },
        {
            value: 'Medium',
            label: 'Medium',
            dotColor: 'bg-risk-medium',
            activeColor: 'text-risk-medium',
            activeBg: 'bg-risk-medium-bg',
        },
        {
            value: 'Low',
            label: 'Low',
            dotColor: 'bg-risk-low',
            activeColor: 'text-risk-low',
            activeBg: 'bg-risk-low-bg',
        },
    ];

export function RiskFilter({ value, onChange, counts }: RiskFilterProps) {
    const getCount = (filterValue: FilterValue): number => {
        switch (filterValue) {
            case 'all': return counts.all;
            case 'High': return counts.high;
            case 'Medium': return counts.medium;
            case 'Low': return counts.low;
        }
    };

    return (
        <div
            className="inline-flex items-center gap-1 bg-dark-300 p-1 rounded-xl"
            role="group"
            aria-label="Filter tasks by risk level"
        >
            {FILTERS.map((filter) => {
                const isActive = value === filter.value;
                const count = getCount(filter.value);

                return (
                    <button
                        key={filter.value}
                        onClick={() => onChange(filter.value)}
                        className={`
                            flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium 
                            transition-all duration-150
                            ${isActive
                                ? `${filter.activeBg} ${filter.activeColor} shadow-sm`
                                : 'text-light-400 hover:text-light-200 hover:bg-dark-400/50'
                            }
                        `}
                        aria-pressed={isActive}
                        aria-label={`Filter by ${filter.label} risk: ${count} tasks`}
                    >
                        {/* Colored dot indicator */}
                        <span className={`w-2 h-2 rounded-full ${filter.dotColor} ${isActive ? 'ring-2 ring-offset-1 ring-offset-transparent ring-current opacity-100' : 'opacity-60'}`} />

                        {/* Label */}
                        <span>{filter.label}</span>

                        {/* Count badge */}
                        <span className={`
                            text-xs tabular-nums px-1.5 py-0.5 rounded-md font-semibold
                            ${isActive
                                ? 'bg-black/20 ' + filter.activeColor
                                : 'bg-dark-500 text-light-400'
                            }
                        `}>
                            {count}
                        </span>
                    </button>
                );
            })}
        </div>
    );
}
