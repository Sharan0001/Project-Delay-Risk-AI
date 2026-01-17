/**
 * History Page - Dark Theme
 * 
 * Displays analysis history with:
 * - List of past analyses with metadata
 * - Scenario and risk breakdown
 * - Ability to reload and view past results
 */

import { useNavigate } from 'react-router-dom';
import {
    History as HistoryIcon,
    Calendar,
    BarChart2,
    AlertTriangle,
    AlertCircle,
    CheckCircle,
    RefreshCw,
    ChevronRight,
    Eye
} from 'lucide-react';

import { useHistory, useLoadAnalysis } from '../hooks';
import type { AnalysisRecord, WhatIfScenario } from '../api';
import { SCENARIO_LABELS } from '../api';

export function History() {
    const navigate = useNavigate();
    const { data, isLoading, error } = useHistory(50);
    const loadAnalysis = useLoadAnalysis();

    // Format timestamp for display - convert UTC to local timezone
    const formatDate = (timestamp: string): string => {
        // Ensure the timestamp is treated as UTC if no timezone specified
        const utcTimestamp = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
        const date = new Date(utcTimestamp);
        return date.toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    // Handle loading a past analysis
    const handleViewAnalysis = (record: AnalysisRecord) => {
        loadAnalysis.mutate(record.id, {
            onSuccess: () => {
                // Navigate to analysis page to view
                navigate('/analysis');
            }
        });
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="animate-fade-in">
                <header className="mb-6">
                    <h1 className="text-2xl font-bold text-light-100">Analysis History</h1>
                    <p className="text-light-300 mt-1">Loading past analyses...</p>
                </header>
                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="card p-4">
                            <div className="skeleton h-6 w-48 mb-2" />
                            <div className="skeleton h-4 w-32" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="animate-fade-in">
                <header className="mb-6">
                    <h1 className="text-2xl font-bold text-light-100">Analysis History</h1>
                </header>
                <div className="card p-8 text-center">
                    <AlertTriangle className="w-12 h-12 text-risk-high mx-auto mb-4" />
                    <h2 className="text-lg font-semibold text-light-100">Failed to Load History</h2>
                    <p className="text-light-300 mt-2">
                        {error instanceof Error ? error.message : 'Unknown error'}
                    </p>
                </div>
            </div>
        );
    }

    const analyses = data?.analyses ?? [];

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <header className="mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-light-100">
                            Analysis History
                        </h1>
                        <p className="text-light-300 mt-1">
                            {analyses.length} past analyses
                        </p>
                    </div>
                </div>
            </header>

            {/* History List */}
            {analyses.length > 0 ? (
                <div className="space-y-3">
                    {analyses.map((record) => (
                        <HistoryCard
                            key={record.id}
                            record={record}
                            formatDate={formatDate}
                            onView={() => handleViewAnalysis(record)}
                            isLoading={loadAnalysis.isPending && loadAnalysis.variables === record.id}
                        />
                    ))}
                </div>
            ) : (
                /* Empty state */
                <div className="card p-12 text-center">
                    <div className="w-16 h-16 bg-dark-300 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <HistoryIcon className="w-8 h-8 text-light-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-light-100 mb-2">
                        No Analysis History
                    </h2>
                    <p className="text-light-300 mb-6">
                        Run your first analysis from the Dashboard to see it here.
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="btn-primary inline-flex items-center gap-2"
                    >
                        Go to Dashboard
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            )}
        </div>
    );
}

// Individual history card component
interface HistoryCardProps {
    record: AnalysisRecord;
    formatDate: (ts: string) => string;
    onView: () => void;
    isLoading: boolean;
}

function HistoryCard({ record, formatDate, onView, isLoading }: HistoryCardProps) {
    const scenarioLabel = record.what_if_scenario
        ? SCENARIO_LABELS[record.what_if_scenario as WhatIfScenario]
        : 'Baseline';

    return (
        <div className="card card-hover p-4">
            <div className="flex items-center justify-between">
                {/* Left: Metadata */}
                <div className="flex items-center gap-4">
                    {/* ID Badge */}
                    <div className="w-12 h-12 bg-primary-500/15 rounded-xl flex items-center justify-center">
                        <span className="text-lg font-bold text-primary-400">
                            #{record.id}
                        </span>
                    </div>

                    {/* Info */}
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-light-100">
                                {record.num_tasks} Tasks Analyzed
                            </span>
                            <span className="text-xs px-2 py-0.5 bg-dark-400 rounded text-light-300">
                                {record.model_type}
                            </span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-light-400">
                            <span className="flex items-center gap-1">
                                <Calendar className="w-3.5 h-3.5" />
                                {formatDate(record.created_at)}
                            </span>
                            <span className="flex items-center gap-1">
                                <BarChart2 className="w-3.5 h-3.5" />
                                {scenarioLabel}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Center: Risk Distribution */}
                <div className="flex items-center gap-4">
                    <RiskCounter
                        icon={AlertTriangle}
                        count={record.high_risk_count}
                        color="text-risk-high"
                        bgColor="bg-risk-high/15"
                        label="High"
                    />
                    <RiskCounter
                        icon={AlertCircle}
                        count={record.medium_risk_count}
                        color="text-risk-medium"
                        bgColor="bg-risk-medium/15"
                        label="Medium"
                    />
                    <RiskCounter
                        icon={CheckCircle}
                        count={record.low_risk_count}
                        color="text-risk-low"
                        bgColor="bg-risk-low/15"
                        label="Low"
                    />
                </div>

                {/* Right: Actions */}
                <button
                    onClick={onView}
                    disabled={isLoading}
                    className="btn-secondary flex items-center gap-2"
                >
                    {isLoading ? (
                        <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Loading...
                        </>
                    ) : (
                        <>
                            <Eye className="w-4 h-4" />
                            View
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

// Risk counter mini component
function RiskCounter({
    icon: Icon,
    count,
    color,
    bgColor,
    label
}: {
    icon: typeof AlertTriangle;
    count: number;
    color: string;
    bgColor: string;
    label: string;
}) {
    return (
        <div className="text-center">
            <div className={`${bgColor} rounded-xl px-3 py-2 mb-1`}>
                <div className="flex items-center gap-1.5">
                    <Icon className={`w-4 h-4 ${color}`} />
                    <span className={`font-bold ${color}`}>{count}</span>
                </div>
            </div>
            <span className="text-xs text-light-400">{label}</span>
        </div>
    );
}
