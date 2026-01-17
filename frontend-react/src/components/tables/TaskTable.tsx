/**
 * Task Results Table Component - Dark Theme
 * 
 * Displays analysis results in a sortable, filterable table with:
 * - Risk level badges
 * - Delay probability percentages
 * - Key reason preview
 * - Click to select functionality
 * - Keyboard navigation (↑↓ Enter, Escape)
 */

import { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { RiskBadge } from '../badges';
import type { TaskRiskResult, RiskLevel } from '../../api';

interface TaskTableProps {
    results: TaskRiskResult[];
    selectedTaskId?: string;
    onTaskSelect: (task: TaskRiskResult) => void;
}

type SortField = 'task_id' | 'risk_level' | 'risk_score' | 'delay_probability';
type SortDirection = 'asc' | 'desc';

// Risk level sort order (High > Medium > Low)
const RISK_ORDER: Record<RiskLevel, number> = {
    High: 3,
    Medium: 2,
    Low: 1,
};

export function TaskTable({ results, selectedTaskId, onTaskSelect }: TaskTableProps) {
    const [sortField, setSortField] = useState<SortField>('risk_score');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
    const [focusedIndex, setFocusedIndex] = useState<number>(-1);

    // Ref to the table body for keyboard navigation
    const tbodyRef = useRef<HTMLTableSectionElement>(null);

    // Handle column header click for sorting
    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection(field === 'task_id' ? 'asc' : 'desc');
        }
    };

    // Sort the results
    const sortedResults = useMemo(() => {
        return [...results].sort((a, b) => {
            let comparison = 0;

            switch (sortField) {
                case 'task_id':
                    comparison = a.task_id.localeCompare(b.task_id, undefined, { numeric: true });
                    break;
                case 'risk_level':
                    comparison = RISK_ORDER[a.risk_level] - RISK_ORDER[b.risk_level];
                    break;
                case 'risk_score':
                    comparison = a.risk_score - b.risk_score;
                    break;
                case 'delay_probability':
                    comparison = a.delay_probability - b.delay_probability;
                    break;
            }

            return sortDirection === 'asc' ? comparison : -comparison;
        });
    }, [results, sortField, sortDirection]);

    // Keyboard navigation handler
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (sortedResults.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setFocusedIndex(prev => {
                    const next = prev < sortedResults.length - 1 ? prev + 1 : prev;
                    return next;
                });
                break;
            case 'ArrowUp':
                e.preventDefault();
                setFocusedIndex(prev => {
                    const next = prev > 0 ? prev - 1 : 0;
                    return next;
                });
                break;
            case 'Enter':
                e.preventDefault();
                if (focusedIndex >= 0 && focusedIndex < sortedResults.length) {
                    onTaskSelect(sortedResults[focusedIndex]);
                }
                break;
            case 'Escape':
                e.preventDefault();
                setFocusedIndex(-1);
                break;
        }
    }, [focusedIndex, sortedResults, onTaskSelect]);

    // Attach keyboard listener to tbody
    useEffect(() => {
        const tbody = tbodyRef.current;
        if (!tbody) return;

        tbody.addEventListener('keydown', handleKeyDown);
        return () => tbody.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    // Scroll focused row into view
    useEffect(() => {
        if (focusedIndex < 0 || !tbodyRef.current) return;

        const rows = tbodyRef.current.querySelectorAll('tr');
        const row = rows[focusedIndex];
        row?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }, [focusedIndex]);

    // Sync focused index with selected task
    useEffect(() => {
        if (selectedTaskId) {
            const idx = sortedResults.findIndex(t => t.task_id === selectedTaskId);
            if (idx >= 0) setFocusedIndex(idx);
        }
    }, [selectedTaskId, sortedResults]);

    // Render sort indicator
    const SortIndicator = ({ field }: { field: SortField }) => {
        if (sortField !== field) {
            return <ChevronsUpDown className="w-4 h-4 text-light-400" />;
        }
        return sortDirection === 'asc'
            ? <ChevronUp className="w-4 h-4 text-primary-400" />
            : <ChevronDown className="w-4 h-4 text-primary-400" />;
    };

    if (results.length === 0) {
        return (
            <div className="card p-8 text-center">
                <p className="text-light-300">No analysis results available.</p>
                <p className="text-sm text-light-400 mt-1">
                    Run an analysis from the dashboard to see results here.
                </p>
            </div>
        );
    }

    return (
        <div className="card overflow-hidden">
            {/* Keyboard hint */}
            <div className="px-4 py-2.5 bg-dark-300/50 border-b border-dark-400/50 text-xs text-light-400 flex items-center gap-4">
                <span>Navigate: <kbd className="px-1.5 py-0.5 bg-dark-400 rounded text-light-300 font-mono">↑</kbd> <kbd className="px-1.5 py-0.5 bg-dark-400 rounded text-light-300 font-mono">↓</kbd></span>
                <span>Select: <kbd className="px-1.5 py-0.5 bg-dark-400 rounded text-light-300 font-mono">Enter</kbd></span>
                <span>Clear: <kbd className="px-1.5 py-0.5 bg-dark-400 rounded text-light-300 font-mono">Esc</kbd></span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="bg-dark-300/30 border-b border-dark-400/50">
                            <HeaderCell
                                label="Task ID"
                                field="task_id"
                                onSort={handleSort}
                                indicator={<SortIndicator field="task_id" />}
                            />
                            <HeaderCell
                                label="Risk Level"
                                field="risk_level"
                                onSort={handleSort}
                                indicator={<SortIndicator field="risk_level" />}
                            />
                            <HeaderCell
                                label="Risk Score"
                                field="risk_score"
                                onSort={handleSort}
                                indicator={<SortIndicator field="risk_score" />}
                            />
                            <HeaderCell
                                label="Delay Probability"
                                field="delay_probability"
                                onSort={handleSort}
                                indicator={<SortIndicator field="delay_probability" />}
                            />
                            <th className="px-4 py-3 text-left text-xs font-semibold text-light-400 uppercase tracking-wider">
                                Key Reason
                            </th>
                        </tr>
                    </thead>
                    <tbody
                        ref={tbodyRef}
                        tabIndex={0}
                        className="divide-y divide-dark-400/30 focus:outline-none"
                        role="listbox"
                        aria-label="Task results"
                    >
                        {sortedResults.map((task, index) => (
                            <tr
                                key={task.task_id}
                                onClick={() => {
                                    setFocusedIndex(index);
                                    onTaskSelect(task);
                                }}
                                role="option"
                                aria-selected={selectedTaskId === task.task_id}
                                aria-label={`${task.task_id}: ${task.risk_level} risk, ${task.risk_score} score`}
                                className={`
                                    cursor-pointer transition-all duration-150
                                    ${selectedTaskId === task.task_id
                                        ? 'bg-primary-500/10 border-l-2 border-l-primary-500'
                                        : focusedIndex === index
                                            ? 'bg-dark-300/50 ring-1 ring-inset ring-primary-500/30'
                                            : 'hover:bg-dark-300/30'
                                    }
                                `}
                            >
                                <td className="px-4 py-3">
                                    <span className="font-mono text-sm font-medium text-light-100">
                                        {task.task_id}
                                    </span>
                                </td>
                                <td className="px-4 py-3">
                                    <RiskBadge level={task.risk_level} size="sm" />
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-3">
                                        <div className="w-16 h-2 bg-dark-400/50 rounded-full overflow-hidden">
                                            <motion.div
                                                className={`h-full rounded-full ${getScoreBarColor(task.risk_score)}`}
                                                initial={{ width: 0 }}
                                                animate={{ width: `${task.risk_score}%` }}
                                                transition={{ duration: 0.4, ease: [0, 0, 0.2, 1], delay: index * 0.03 }}
                                            />
                                        </div>
                                        <span className="text-sm font-semibold text-light-200 tabular-nums">
                                            {task.risk_score}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <ProbabilityCell task={task} />
                                </td>
                                <td className="px-4 py-3">
                                    <span className="text-sm text-light-300 truncate block max-w-xs">
                                        {task.reasons[0] || 'No specific reason'}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// Header cell component with sort functionality
function HeaderCell({
    label,
    field,
    onSort,
    indicator
}: {
    label: string;
    field: SortField;
    onSort: (field: SortField) => void;
    indicator: React.ReactNode;
}) {
    return (
        <th
            className="px-4 py-3 text-left text-xs font-semibold text-light-400 uppercase tracking-wider cursor-pointer hover:bg-dark-300/30 transition-colors select-none"
            onClick={() => onSort(field)}
        >
            <div className="flex items-center gap-1.5">
                {label}
                {indicator}
            </div>
        </th>
    );
}

// Get color for risk score bar
function getScoreBarColor(score: number): string {
    if (score >= 60) return 'bg-risk-high';
    if (score >= 40) return 'bg-risk-medium';
    return 'bg-risk-low';
}

// Get color for probability text
function getProbabilityColor(probability: number): string {
    if (probability >= 0.6) return 'text-risk-high';
    if (probability >= 0.4) return 'text-risk-medium';
    return 'text-risk-low';
}

// Probability cell that shows what-if adjusted values when available
function ProbabilityCell({ task }: { task: TaskRiskResult }) {
    const hasWhatIf = task.what_if_impact && task.what_if_impact.probability_reduction > 0;

    if (hasWhatIf && task.what_if_impact) {
        const newProb = task.what_if_impact.new_delay_probability;
        const reduction = task.what_if_impact.probability_reduction;

        return (
            <div className="flex items-center gap-2">
                {/* Original probability struck through */}
                <motion.span
                    className="text-sm text-light-400 line-through tabular-nums"
                    initial={{ opacity: 1 }}
                    animate={{ opacity: 0.5 }}
                    transition={{ duration: 0.3 }}
                >
                    {(task.delay_probability * 100).toFixed(0)}%
                </motion.span>
                {/* New probability */}
                <motion.span
                    className={`text-sm font-semibold tabular-nums ${getProbabilityColor(newProb)}`}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: 0.1 }}
                >
                    {(newProb * 100).toFixed(1)}%
                </motion.span>
                {/* Reduction indicator with scale-in */}
                <motion.span
                    className="text-xs text-risk-low font-semibold bg-risk-low-bg px-1.5 py-0.5 rounded"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.15, delay: 0.2, ease: [0, 0, 0.2, 1] }}
                >
                    ↓{(reduction * 100).toFixed(0)}%
                </motion.span>
            </div>
        );
    }

    // No what-if scenario - show baseline
    return (
        <span className={`text-sm font-semibold tabular-nums ${getProbabilityColor(task.delay_probability)}`}>
            {(task.delay_probability * 100).toFixed(1)}%
        </span>
    );
}
