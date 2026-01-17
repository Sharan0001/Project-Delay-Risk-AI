/**
 * Analysis Results Page - Dark Theme
 * 
 * Displays analysis results with:
 * - Summary statistics bar
 * - Filter tabs by risk level
 * - Sortable results table
 * - Task detail panel on row click
 */

import { useState, useMemo } from 'react';
import {
    Play,
    RefreshCw,
    AlertTriangle,
    AlertCircle,
    CheckCircle,
    BarChart2
} from 'lucide-react';

import { useAnalysis } from '../hooks';
import { TaskTable } from '../components/tables';
import { RiskFilter, TaskDetailPanel, type FilterValue } from '../components/common';
import type { TaskRiskResult, WhatIfScenario } from '../api';
import { calculateRiskSummary, SCENARIO_LABELS } from '../api';

export function Analysis() {
    const { runAnalysis, results, isLoading } = useAnalysis();

    // Local state
    const [filter, setFilter] = useState<FilterValue>('all');
    const [selectedTask, setSelectedTask] = useState<TaskRiskResult | null>(null);
    const [whatIfScenario, setWhatIfScenario] = useState<WhatIfScenario | null>(null);

    // Calculate risk summary
    const summary = useMemo(() => calculateRiskSummary(results), [results]);

    // Filter results by risk level
    const filteredResults = useMemo(() => {
        if (filter === 'all') return results;
        return results.filter(r => r.risk_level === filter);
    }, [results, filter]);

    // Handle run analysis
    const handleRunAnalysis = () => {
        runAnalysis(whatIfScenario);
    };

    // Handle task selection
    const handleTaskSelect = (task: TaskRiskResult) => {
        setSelectedTask(task);
    };

    // Close detail panel
    const handleClosePanel = () => {
        setSelectedTask(null);
    };

    return (
        <div className="animate-fade-in">
            {/* Header with actions */}
            <header className="mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-light-100">
                            Analysis Results
                        </h1>
                        <p className="text-light-300 mt-1">
                            {results.length > 0
                                ? `${results.length} tasks analyzed`
                                : 'Run an analysis to see results'
                            }
                        </p>
                    </div>

                    {/* Run Analysis Controls */}
                    <div className="flex items-center gap-3">
                        <select
                            value={whatIfScenario || ''}
                            onChange={(e) => setWhatIfScenario(e.target.value as WhatIfScenario || null)}
                            className="select"
                        >
                            <option value="">No scenario (baseline)</option>
                            {Object.entries(SCENARIO_LABELS).map(([key, label]) => (
                                <option key={key} value={key}>{label}</option>
                            ))}
                        </select>

                        <button
                            onClick={handleRunAnalysis}
                            disabled={isLoading}
                            className="btn-primary flex items-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    Running...
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4" />
                                    Run Analysis
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </header>

            {/* Results Section */}
            {results.length > 0 ? (
                <>
                    {/* Summary Bar */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <SummaryCard
                            icon={BarChart2}
                            iconColor="text-primary-400"
                            iconBg="bg-primary-500/10"
                            label="Total Tasks"
                            value={summary.total}
                        />
                        <SummaryCard
                            icon={AlertTriangle}
                            iconColor="text-risk-high"
                            iconBg="bg-risk-high-bg"
                            label="High Risk"
                            value={summary.high}
                            percentage={summary.highPercentage}
                        />
                        <SummaryCard
                            icon={AlertCircle}
                            iconColor="text-risk-medium"
                            iconBg="bg-risk-medium-bg"
                            label="Medium Risk"
                            value={summary.medium}
                            percentage={summary.mediumPercentage}
                        />
                        <SummaryCard
                            icon={CheckCircle}
                            iconColor="text-risk-low"
                            iconBg="bg-risk-low-bg"
                            label="Low Risk"
                            value={summary.low}
                            percentage={summary.lowPercentage}
                        />
                    </div>

                    {/* Filter Tabs */}
                    <div className="mb-4">
                        <RiskFilter
                            value={filter}
                            onChange={setFilter}
                            counts={{
                                all: summary.total,
                                high: summary.high,
                                medium: summary.medium,
                                low: summary.low,
                            }}
                        />
                    </div>

                    {/* Results Table */}
                    <TaskTable
                        results={filteredResults}
                        selectedTaskId={selectedTask?.task_id}
                        onTaskSelect={handleTaskSelect}
                    />

                    {/* Task Detail Panel */}
                    <TaskDetailPanel
                        task={selectedTask}
                        onClose={handleClosePanel}
                    />
                </>
            ) : (
                /* Empty State */
                <div className="card p-12 text-center">
                    <div className="w-16 h-16 bg-dark-300 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <BarChart2 className="w-8 h-8 text-light-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-light-100 mb-2">
                        No Analysis Results
                    </h2>
                    <p className="text-light-300 mb-6 max-w-md mx-auto">
                        Run an analysis to see task-level risk assessments with explanations
                        and actionable recommendations.
                    </p>
                    <button
                        onClick={handleRunAnalysis}
                        disabled={isLoading}
                        className="btn-primary inline-flex items-center gap-2"
                    >
                        {isLoading ? (
                            <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                Running...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" />
                                Run First Analysis
                            </>
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}

// Summary card component
function SummaryCard({
    icon: Icon,
    iconColor,
    iconBg,
    label,
    value,
    percentage,
}: {
    icon: typeof BarChart2;
    iconColor: string;
    iconBg: string;
    label: string;
    value: number;
    percentage?: number;
}) {
    return (
        <div className="card p-4 flex items-center gap-4">
            <div className={`p-2.5 rounded-xl ${iconBg}`}>
                <Icon className={`w-5 h-5 ${iconColor}`} />
            </div>
            <div>
                <div className="text-sm text-light-300">{label}</div>
                <div className="flex items-baseline gap-2">
                    <span className="text-xl font-bold text-light-100">{value}</span>
                    {percentage !== undefined && (
                        <span className="text-xs text-light-400">
                            ({percentage.toFixed(0)}%)
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
