/**
 * Dashboard Page
 * 
 * Landing page showing:
 * - System status (backend health)
 * - Aggregate statistics
 * - Risk distribution chart
 * - Run analysis button
 */

import { useNavigate } from 'react-router-dom';
import {
    Activity,
    BarChart3,
    Clock,
    AlertTriangle,
    ChevronRight,
    Play,
    RefreshCw
} from 'lucide-react';

import { useHealth, useStats, useAnalysis } from '../hooks';
import { StatusBadge, StatCard } from '../components/common';
import { RiskDistributionChart } from '../components/charts';

export function Dashboard() {
    const navigate = useNavigate();
    const health = useHealth();
    const { data: stats, isLoading: statsLoading } = useStats();
    const { runAnalysis, isLoading: analysisLoading } = useAnalysis();

    // Format last analysis time - convert UTC to local timezone
    const formatLastAnalysis = (timestamp: string | null): string => {
        if (!timestamp) return 'Never';
        // Ensure the timestamp is treated as UTC if no timezone specified
        const utcTimestamp = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
        const date = new Date(utcTimestamp);
        return date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    // Handle run analysis
    const handleRunAnalysis = () => {
        runAnalysis(null, {
            onSuccess: () => {
                navigate('/analysis');
            },
        });
    };

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <header className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-light-100">
                            Risk Intelligence Dashboard
                        </h1>
                        <p className="text-light-300 mt-1">
                            AI-powered project delay risk analysis and decision support
                        </p>
                    </div>
                    <StatusBadge
                        isConnected={health.isConnected}
                        isLoading={health.isLoading}
                        version={health.version}
                    />
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatCard
                    label="Total Analyses"
                    value={stats?.total_analyses ?? 0}
                    icon={BarChart3}
                    iconColor="text-primary-400"
                    iconBg="bg-primary-500/10"
                    tooltip="Number of risk analysis runs performed"
                    isLoading={statsLoading}
                    index={0}
                />
                <StatCard
                    label="Tasks Analyzed"
                    value={stats?.total_tasks_analyzed ?? 0}
                    icon={Activity}
                    iconColor="text-violet-400"
                    iconBg="bg-violet-500/10"
                    tooltip="Total individual tasks evaluated for risk"
                    isLoading={statsLoading}
                    index={1}
                />
                <StatCard
                    label="High Risk Tasks"
                    value={stats?.total_high_risk ?? 0}
                    icon={AlertTriangle}
                    iconColor="text-risk-high"
                    iconBg="bg-risk-high-bg"
                    tooltip="Tasks with risk score ≥60 requiring immediate attention"
                    isLoading={statsLoading}
                    index={2}
                />
                <StatCard
                    label="Last Analysis"
                    value={formatLastAnalysis(stats?.last_analysis ?? null)}
                    icon={Clock}
                    iconColor="text-light-300"
                    iconBg="bg-dark-400/50"
                    tooltip="When the most recent analysis was run"
                    isLoading={statsLoading}
                    index={3}
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Risk Distribution Card */}
                <div className="lg:col-span-2 card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-light-100">
                            Risk Distribution
                        </h2>
                        <span className="text-xs text-light-400">
                            All-time aggregate
                        </span>
                    </div>

                    <RiskDistributionChart
                        high={stats?.total_high_risk ?? 0}
                        medium={stats?.total_medium_risk ?? 0}
                        low={stats?.total_low_risk ?? 0}
                    />
                </div>

                {/* Quick Actions Card */}
                <div className="card p-6">
                    <h2 className="text-lg font-semibold text-light-100 mb-4">
                        Quick Actions
                    </h2>

                    <div className="space-y-3">
                        {/* Run New Analysis */}
                        <button
                            onClick={handleRunAnalysis}
                            disabled={!health.isConnected || analysisLoading}
                            className="w-full btn-primary flex items-center justify-center gap-2"
                        >
                            {analysisLoading ? (
                                <>
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    Running Analysis...
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4" />
                                    Run New Analysis
                                </>
                            )}
                        </button>

                        {/* View Results */}
                        <button
                            onClick={() => navigate('/analysis')}
                            className="w-full btn-secondary flex items-center justify-between"
                        >
                            <span>View Analysis Results</span>
                            <ChevronRight className="w-4 h-4" />
                        </button>

                        {/* View History */}
                        <button
                            onClick={() => navigate('/history')}
                            className="w-full btn-secondary flex items-center justify-between"
                        >
                            <span>Analysis History</span>
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Backend Status Message */}
                    {!health.isConnected && !health.isLoading && (
                        <div className="mt-4 p-3 bg-risk-high-bg rounded-lg">
                            <p className="text-sm text-risk-high">
                                Backend is not connected. Start the server:
                            </p>
                            <code className="text-xs text-surface-600 mt-1 block font-mono">
                                python -m uvicorn backend.app:app --reload
                            </code>
                        </div>
                    )}
                </div>
            </div>

            {/* Feature Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                <FeatureCard
                    title="Hybrid Risk Scoring"
                    description="Combines expert rules with ML predictions for interpretable risk assessment"
                    icon="🎯"
                />
                <FeatureCard
                    title="What-If Analysis"
                    description="Simulate scenarios like adding resources or reducing dependencies"
                    icon="🔮"
                />
                <FeatureCard
                    title="Actionable Insights"
                    description="Get prioritized recommendations with clear rationale"
                    icon="💡"
                />
            </div>
        </div>
    );
}

// Feature highlight card
function FeatureCard({
    title,
    description,
    icon
}: {
    title: string;
    description: string;
    icon: string;
}) {
    return (
        <div className="card p-4 border-l-4 border-l-primary-500">
            <div className="flex items-start gap-3">
                <span className="text-2xl">{icon}</span>
                <div>
                    <h3 className="font-semibold text-surface-800">{title}</h3>
                    <p className="text-sm text-surface-500 mt-1">{description}</p>
                </div>
            </div>
        </div>
    );
}
