/**
 * Task Detail Panel Component
 * 
 * Enhanced slide-out panel showing full task details:
 * - Risk summary with visual emphasis
 * - Collapsible sections (Risk Factors / Actions)
 * - Primary Risk Driver badge on first critical factor
 * - What-if impact with before/after comparison
 * - Keyboard support (Escape to close)
 */

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
    X,
    AlertTriangle,
    AlertCircle,
    CheckCircle,
    Target,
    Lightbulb,
    ChevronDown,
    ChevronRight,
    TrendingDown,
    Zap
} from 'lucide-react';
import { RiskBadge } from '../badges';
import type { TaskRiskResult } from '../../api';
import { panelVariants } from '../../lib/motion';

interface TaskDetailPanelProps {
    task: TaskRiskResult | null;
    onClose: () => void;
}

export function TaskDetailPanel({ task, onClose }: TaskDetailPanelProps) {
    const [factorsExpanded, setFactorsExpanded] = useState(true);
    const [actionsExpanded, setActionsExpanded] = useState(true);

    // Keyboard handler for Escape
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            onClose();
        }
    }, [onClose]);

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    // Focus trap - prevent scroll on body when panel is open
    useEffect(() => {
        if (task) {
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [task]);

    if (!task) return null;

    // Sort reasons by severity (critical first)
    const sortedReasons = [...task.reasons].sort((a, b) => {
        const order = { critical: 0, warning: 1, info: 2 };
        return order[getSeverityFromReason(a)] - order[getSeverityFromReason(b)];
    });

    // Sort actions by priority (HIGH first)
    const sortedActions = [...task.recommended_actions].sort((a, b) => {
        const order = { HIGH: 0, MEDIUM: 1, LOW: 2 };
        return order[getPriorityFromAction(a)] - order[getPriorityFromAction(b)];
    });

    return (
        <>
            {/* Backdrop */}
            <motion.div
                className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
                onClick={onClose}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
            />

            {/* Panel - slides in from right */}
            <motion.div
                className="fixed right-0 top-0 h-full w-full max-w-lg bg-dark-200 shadow-2xl z-50 overflow-y-auto border-l border-dark-400/50"
                variants={panelVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
            >
                {/* Header */}
                <div className="sticky top-0 bg-dark-200 border-b border-dark-400/50 px-6 py-4 flex items-center justify-between z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-dark-400 rounded-xl flex items-center justify-center">
                            <span className="font-mono text-sm font-bold text-light-100">
                                {task.task_id}
                            </span>
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-light-100">
                                Task Details
                            </h2>
                            <div className="flex items-center gap-2 mt-0.5">
                                <RiskBadge level={task.risk_level} size="sm" />
                                <span className="text-xs text-light-400">
                                    Score: {task.risk_score}
                                </span>
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-dark-400 rounded-lg transition-colors"
                        aria-label="Close panel"
                    >
                        <X className="w-5 h-5 text-light-400" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Risk Metrics */}
                    <section>
                        <div className="grid grid-cols-2 gap-4">
                            <MetricCard
                                label="Risk Score"
                                value={task.risk_score}
                                subtext="out of 100"
                                color={getRiskColor(task.risk_level)}
                            />
                            <MetricCard
                                label="Delay Probability"
                                value={`${(task.delay_probability * 100).toFixed(1)}%`}
                                subtext="chance of delay"
                                color={task.delay_probability >= 0.6 ? 'text-risk-high' :
                                    task.delay_probability >= 0.4 ? 'text-risk-medium' : 'text-risk-low'}
                            />
                        </div>
                    </section>

                    {/* Risk Factors - Collapsible */}
                    <CollapsibleSection
                        title="Risk Factors"
                        icon={Target}
                        iconColor="text-primary-500"
                        count={task.reasons.length}
                        expanded={factorsExpanded}
                        onToggle={() => setFactorsExpanded(!factorsExpanded)}
                    >
                        {sortedReasons.length > 0 ? (
                            <div className="space-y-2">
                                {sortedReasons.map((reason, idx) => {
                                    const severity = getSeverityFromReason(reason);
                                    const isPrimary = idx === 0 && severity === 'critical';
                                    return (
                                        <ReasonCard
                                            key={idx}
                                            reason={reason}
                                            severity={severity}
                                            isPrimary={isPrimary}
                                        />
                                    );
                                })}
                            </div>
                        ) : (
                            <p className="text-sm text-light-400 italic py-2">
                                No specific risk factors identified
                            </p>
                        )}
                    </CollapsibleSection>

                    {/* Recommended Actions - Collapsible */}
                    <CollapsibleSection
                        title="Recommended Actions"
                        icon={Lightbulb}
                        iconColor="text-amber-500"
                        count={task.recommended_actions.length}
                        expanded={actionsExpanded}
                        onToggle={() => setActionsExpanded(!actionsExpanded)}
                    >
                        {sortedActions.length > 0 ? (
                            <div className="space-y-2">
                                {sortedActions.map((action, idx) => (
                                    <ActionCard
                                        key={idx}
                                        action={action}
                                        priority={getPriorityFromAction(action)}
                                        index={idx + 1}
                                    />
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-light-400 italic py-2">
                                No specific actions recommended
                            </p>
                        )}
                    </CollapsibleSection>

                    {/* What-If Impact - Enhanced */}
                    {task.what_if_impact && (
                        <section className="border-t border-dark-400/30 pt-6">
                            <div className="flex items-center gap-2 mb-4">
                                <TrendingDown className="w-4 h-4 text-risk-low" />
                                <h3 className="text-sm font-medium text-light-400 uppercase tracking-wider">
                                    What-If Impact
                                </h3>
                            </div>

                            <WhatIfComparison
                                scenario={task.what_if_impact.scenario}
                                originalProbability={task.delay_probability}
                                newProbability={task.what_if_impact.new_delay_probability}
                                reduction={task.what_if_impact.probability_reduction}
                            />
                        </section>
                    )}
                </div>

                {/* Footer hint */}
                <div className="sticky bottom-0 bg-dark-300 border-t border-dark-400/50 px-6 py-3">
                    <p className="text-xs text-light-400 text-center">
                        Press <kbd className="px-1.5 py-0.5 bg-dark-400 rounded font-mono text-light-300">Esc</kbd> to close
                    </p>
                </div>
            </motion.div>
        </>
    );
}

// Metric card with large value display
function MetricCard({
    label,
    value,
    subtext,
    color
}: {
    label: string;
    value: string | number;
    subtext: string;
    color: string;
}) {
    return (
        <div className="bg-dark-300 rounded-xl p-4">
            <div className="text-xs text-light-400 uppercase tracking-wider mb-1">
                {label}
            </div>
            <div className={`text-3xl font-bold tabular-nums ${color}`}>
                {value}
            </div>
            <div className="text-xs text-light-400 mt-0.5">{subtext}</div>
        </div>
    );
}

// Collapsible section wrapper
function CollapsibleSection({
    title,
    icon: Icon,
    iconColor,
    count,
    expanded,
    onToggle,
    children
}: {
    title: string;
    icon: typeof Target;
    iconColor: string;
    count: number;
    expanded: boolean;
    onToggle: () => void;
    children: React.ReactNode;
}) {
    return (
        <section className="border border-dark-400/50 rounded-xl overflow-hidden">
            <button
                onClick={onToggle}
                className="w-full flex items-center justify-between px-4 py-3 bg-dark-300 hover:bg-dark-400/50 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${iconColor}`} />
                    <span className="text-sm font-medium text-light-100">
                        {title}
                    </span>
                    <span className="text-xs bg-dark-400 text-light-300 px-1.5 py-0.5 rounded-full">
                        {count}
                    </span>
                </div>
                {expanded ? (
                    <ChevronDown className="w-4 h-4 text-light-400" />
                ) : (
                    <ChevronRight className="w-4 h-4 text-light-400" />
                )}
            </button>
            {expanded && (
                <div className="p-4 bg-dark-200">
                    {children}
                </div>
            )}
        </section>
    );
}

// Reason card with severity indicator and primary badge
function ReasonCard({
    reason,
    severity,
    isPrimary
}: {
    reason: string;
    severity: 'critical' | 'warning' | 'info';
    isPrimary: boolean;
}) {
    const config = {
        critical: {
            bg: 'bg-risk-high/10',
            border: 'border-l-risk-high',
            icon: AlertTriangle,
            iconColor: 'text-risk-high',
            textColor: 'text-light-100',
        },
        warning: {
            bg: 'bg-risk-medium/10',
            border: 'border-l-risk-medium',
            icon: AlertCircle,
            iconColor: 'text-risk-medium',
            textColor: 'text-light-200',
        },
        info: {
            bg: 'bg-dark-400/30',
            border: 'border-l-light-400',
            icon: CheckCircle,
            iconColor: 'text-light-400',
            textColor: 'text-light-300',
        },
    };

    const { bg, border, icon: Icon, iconColor, textColor } = config[severity];

    return (
        <div className={`${bg} border-l-4 ${border} p-3 rounded-r-lg relative`}>
            {isPrimary && (
                <div className="absolute -top-1 -right-1">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-risk-high text-white text-xs font-medium rounded-full shadow-sm">
                        <Zap className="w-3 h-3" />
                        Primary Driver
                    </span>
                </div>
            )}
            <div className="flex items-start gap-2">
                <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${iconColor}`} />
                <span className={`text-sm ${textColor}`}>{reason}</span>
            </div>
        </div>
    );
}

// Action card with priority badge and step number
function ActionCard({
    action,
    priority,
    index
}: {
    action: string;
    priority: 'HIGH' | 'MEDIUM' | 'LOW';
    index: number;
}) {
    const priorityConfig = {
        HIGH: { bg: 'bg-risk-high', text: 'text-white' },
        MEDIUM: { bg: 'bg-risk-medium', text: 'text-dark-bg' },
        LOW: { bg: 'bg-dark-400', text: 'text-light-300' },
    };

    const { bg, text } = priorityConfig[priority];

    return (
        <div className="flex items-start gap-3 p-3 bg-dark-300/50 rounded-lg">
            <span className="w-6 h-6 flex-shrink-0 bg-dark-400 rounded-full flex items-center justify-center text-xs font-medium text-light-200">
                {index}
            </span>
            <div className="flex-1">
                <span className="text-sm text-light-200">{action}</span>
            </div>
            <span className={`px-2 py-0.5 text-xs font-semibold rounded flex-shrink-0 ${bg} ${text}`}>
                {priority}
            </span>
        </div>
    );
}

// What-If before/after comparison
function WhatIfComparison({
    scenario,
    originalProbability,
    newProbability,
    reduction
}: {
    scenario: string;
    originalProbability: number;
    newProbability: number;
    reduction: number;
}) {
    const reductionPercent = (reduction * 100).toFixed(1);
    const originalPercent = (originalProbability * 100).toFixed(1);
    const newPercent = (newProbability * 100).toFixed(1);

    // Determine if this is a meaningful improvement
    const isSignificant = reduction >= 0.05;

    return (
        <div className="bg-gradient-to-r from-dark-300 to-risk-low/10 rounded-xl p-4 border border-dark-400/50">
            {/* Scenario label */}
            <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-medium text-light-400 uppercase">Scenario:</span>
                <span className="text-sm font-medium text-light-100 capitalize">
                    {scenario.replace(/_/g, ' ')}
                </span>
            </div>

            {/* Before/After comparison */}
            <div className="flex items-center gap-4">
                {/* Before */}
                <div className="flex-1">
                    <div className="text-xs text-light-400 mb-1">Before</div>
                    <div className="text-2xl font-bold text-light-400 line-through tabular-nums">
                        {originalPercent}%
                    </div>
                </div>

                {/* Arrow */}
                <div className="flex flex-col items-center">
                    <div className={`text-xs font-semibold px-2 py-1 rounded ${isSignificant ? 'bg-risk-low text-dark-bg' : 'bg-dark-400 text-light-300'
                        }`}>
                        ↓ {reductionPercent}%
                    </div>
                </div>

                {/* After */}
                <div className="flex-1 text-right">
                    <div className="text-xs text-light-400 mb-1">After</div>
                    <div className="text-2xl font-bold text-risk-low tabular-nums">
                        {newPercent}%
                    </div>
                </div>
            </div>

            {/* Net impact summary */}
            {isSignificant && (
                <div className="mt-4 pt-3 border-t border-dark-400/50">
                    <p className="text-sm text-risk-low font-medium">
                        ✓ This intervention could reduce delay risk by {reductionPercent}%
                    </p>
                </div>
            )}
        </div>
    );
}

// Helper functions
function getRiskColor(level: string): string {
    switch (level) {
        case 'High': return 'text-risk-high';
        case 'Medium': return 'text-risk-medium';
        case 'Low': return 'text-risk-low';
        default: return 'text-surface-600';
    }
}

function getSeverityFromReason(reason: string): 'critical' | 'warning' | 'info' {
    const lowerReason = reason.toLowerCase();
    if (lowerReason.includes('block') || lowerReason.includes('resource') || lowerReason.includes('insufficient')) {
        return 'critical';
    }
    if (lowerReason.includes('dependency') || lowerReason.includes('rework') || lowerReason.includes('stagnation')) {
        return 'warning';
    }
    return 'info';
}

function getPriorityFromAction(action: string): 'HIGH' | 'MEDIUM' | 'LOW' {
    const lowerAction = action.toLowerCase();
    if (lowerAction.includes('allocate') || lowerAction.includes('additional') || lowerAction.includes('root cause')) {
        return 'HIGH';
    }
    if (lowerAction.includes('review') || lowerAction.includes('investigate') || lowerAction.includes('monitoring')) {
        return 'MEDIUM';
    }
    return 'LOW';
}
