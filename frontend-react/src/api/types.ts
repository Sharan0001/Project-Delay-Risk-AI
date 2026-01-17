/**
 * API Type Definitions
 * 
 * These types match the backend API response structures.
 * All types are strictly defined to ensure type safety.
 */

// =============================================================================
// Health & Status Types
// =============================================================================

export interface HealthResponse {
    status: string;
    version: string;
}

export interface StatsResponse {
    total_analyses: number | null;
    total_tasks_analyzed: number | null;
    total_high_risk: number | null;
    total_medium_risk: number | null;
    total_low_risk: number | null;
    last_analysis: string | null;
}

// =============================================================================
// Analysis Types
// =============================================================================

export type RiskLevel = 'High' | 'Medium' | 'Low';

export type WhatIfScenario =
    | 'add_resource'
    | 'reduce_dependencies'
    | 'improve_process';

export interface WhatIfImpact {
    scenario: WhatIfScenario;
    new_delay_probability: number;
    probability_reduction: number;
}

export interface TaskRiskResult {
    task_id: string;
    risk_level: RiskLevel;
    risk_score: number;
    delay_probability: number;
    reasons: string[];
    recommended_actions: string[];
    what_if_impact?: WhatIfImpact | null;
}

export interface AnalyzeRequest {
    what_if?: WhatIfScenario | null;
}

export interface AnalyzeResponse {
    results: TaskRiskResult[];
}

// =============================================================================
// History & Audit Types
// =============================================================================

export interface AnalysisRecord {
    id: number;
    project_id: number | null;
    what_if_scenario: WhatIfScenario | null;
    model_type: string;
    num_tasks: number;
    high_risk_count: number;
    medium_risk_count: number;
    low_risk_count: number;
    created_at: string;
}

export interface AnalysisDetail extends AnalysisRecord {
    results: TaskRiskResult[];
}

export interface HistoryResponse {
    analyses: AnalysisRecord[];
}

// =============================================================================
// Project Import Types
// =============================================================================

export interface Project {
    id: number;
    name: string;
    description: string | null;
    created_at: string;
    updated_at: string;
}

export interface ProjectListResponse {
    projects: Project[];
}

// =============================================================================
// UI Helper Types
// =============================================================================

export interface RiskSummary {
    total: number;
    high: number;
    medium: number;
    low: number;
    highPercentage: number;
    mediumPercentage: number;
    lowPercentage: number;
}

/**
 * Calculates risk summary from analysis results
 */
export function calculateRiskSummary(results: TaskRiskResult[]): RiskSummary {
    const total = results.length;
    const high = results.filter(r => r.risk_level === 'High').length;
    const medium = results.filter(r => r.risk_level === 'Medium').length;
    const low = results.filter(r => r.risk_level === 'Low').length;

    return {
        total,
        high,
        medium,
        low,
        highPercentage: total > 0 ? (high / total) * 100 : 0,
        mediumPercentage: total > 0 ? (medium / total) * 100 : 0,
        lowPercentage: total > 0 ? (low / total) * 100 : 0,
    };
}

/**
 * Scenario display labels
 */
export const SCENARIO_LABELS: Record<WhatIfScenario, string> = {
    add_resource: 'Add Resource',
    reduce_dependencies: 'Reduce Dependencies',
    improve_process: 'Improve Process',
};

/**
 * Scenario descriptions for UI
 */
export const SCENARIO_DESCRIPTIONS: Record<WhatIfScenario, string> = {
    add_resource: 'Simulate adding a new resource to reduce bottlenecks',
    reduce_dependencies: 'Simulate reducing task coupling through refactoring',
    improve_process: 'Simulate process improvements to reduce rework',
};
