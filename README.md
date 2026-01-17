# Project Delay Risk AI — Decision Intelligence System

A system-level AI platform that predicts project task delay risk, explains contributing factors, and recommends mitigations. Designed as a decision support tool, not a dashboard.

---

## Problem Statement

Project delays cost organizations billions annually. Traditional project management tools show what *has* happened—task status, timelines, resource allocation—but rarely anticipate what *will* happen or explain *why* something might fail.

Simple dashboards fall short for three reasons:

1. **Reactive metrics** — They report actuals (tasks overdue, velocity trends) but don't synthesize early warning signals into actionable risk assessments.
2. **No causal reasoning** — A red status tells you a task is at risk; it doesn't explain whether the issue is resource bottlenecks, dependency coupling, or quality-driven rework.
3. **Recommendation gap** — Knowing a task is "high risk" is unhelpful without prioritized actions. Project managers need decision support, not just analytics.

This project addresses the gap between data visibility and decision-making by implementing a **decision intelligence layer**: a system that scores risk, explains its reasoning, simulates interventions, and recommends actions—with deterministic, auditable logic.

---

## System Overview

The platform operates as a closed-loop decision support system:

```
Inputs                  Processing                         Outputs
───────────────────────────────────────────────────────────────────────
Project tasks     →     Feature extraction          →     Risk scores (0-100)
Task events       →     Rule-based reasoning        →     Risk explanations
(blocks, rework,  →     ML probability estimation   →     Recommended actions
progress updates) →     Hybrid score combination    →     What-if comparisons
                  →     Action recommendation       →     Full audit trail
```

**Key behaviors:**
- All outputs are deterministic given the same input
- Every risk score is accompanied by rule-triggered explanations
- What-if scenarios allow intervention simulation without affecting baseline
- The system prioritizes explainability over predictive complexity

---

## Key Design Principles

### Rules as First-Class Citizens

Domain-expert knowledge is encoded as explicit rules, not hidden inside an ML model. Rules are auditable, editable, and provide guaranteed explanations. Example: "If a task has 3+ blocking events, flag as high severity with reason 'Frequent task blocking.'"

### ML as a Supplementary Signal

Two machine learning models are available:
- **Logistic Regression** (default): Linear, fully interpretable coefficients
- **Random Forest**: Non-linear, captures complex patterns, feature importance via impurity reduction

However, ML does not override rules—it supplements them. The final score is a weighted combination: **60% rule-based, 40% ML-based**.

### Determinism Over Randomness

Given identical inputs, the system produces identical outputs. No stochastic sampling, no runtime randomness. This is critical for audit trails and reproducibility.

### Explainability Over Raw Prediction

A 78% delay probability is useless without context. The system returns not just scores but the specific signals that contributed: which rules fired, with what severity, and what the ML model's feature contributions were.

### Decision Support Over Analytics Density

The frontend deliberately avoids chart-heavy dashboards. The goal is a task-level triage interface where each row presents a decision: what is the risk, why, and what should I do about it.

---

## Architecture Overview

The system consists of multiple interconnected modules:

### 1. Simulator (`project_simulator/`)
Generates synthetic project data: tasks, events (progress, blocks, rework), and configurable disruption patterns. Uses a controllable random seed for reproducibility.

### 2. Data Pipeline (`data_pipeline/`)
Validates raw data, normalizes timestamps, and stages inputs for feature extraction. Includes schema validation using Pydantic.

### 3. Feature Engineering (`data_pipeline/features.py`)
Extracts task-level signals from event logs:
- Blocking event counts (total, by reason)
- Rework frequency
- Progress stagnation (max gap between updates)
- Dependency density

### 4. Rules Engine (`models/rules.py`)
Evaluates 5 domain rules against task features. Each rule has a threshold, score contribution (0-25 points), severity level, and human-readable reason. Total rule score caps at 100.

### 5. ML Models (`models/ml_model.py`)
Two interchangeable models with the same interface:
- **DelayRiskModel**: Logistic regression with standardization pipeline. Coefficients provide directional feature impact.
- **DelayRiskRFModel**: Random Forest (200 trees, max depth 6). Feature importance via impurity reduction.

Both output delay probability (0.0–1.0) and support train/predict/evaluate/save/load operations.

### 6. Hybrid Risk Scoring (`models/hybrid_risk.py`)
Combines rule score and ML probability using a weighted formula:
```
final_score = 0.6 × rule_score + 0.4 × (ml_probability × 100)
```
Thresholds classify into High (≥70), Medium (≥40), Low (<40).

### 7. Decision Support (`decision_support/`)
Three sub-modules:
- **actions.py**: Maps triggered risk signals to prioritized action recommendations
- **explain.py**: Generates human-readable explanations combining rules + ML feature importance
- **what_if.py**: Counterfactual simulation engine with three scenarios

### 8. API Layer (`backend/`)
FastAPI application exposing endpoints for analysis, history, statistics, and Prometheus metrics. Includes optional API key authentication and rate limiting.

### 9. Frontend (`frontend-react/`)
React + TypeScript SPA with dark-themed UI. Displays risk-scored task list, filter tabs, sortable columns, slide-out detail panel, and what-if scenario comparison.

---

## Core Features

### Risk Scoring
Each task receives a normalized score (0–100) and classification (Low / Medium / High).

### Rule-Based Explanations
Every triggered rule is surfaced with:
- Human-readable reason (e.g., "Insufficient resource availability")
- Severity level (critical / warning)
- Underlying rationale

### ML Feature Contribution
Model coefficients (Logistic Regression) or feature importance (Random Forest) indicate which features increase or decrease predicted delay probability. The explain module formats this directionally (e.g., "total_blocked_events increases risk").

### What-If Scenario Analysis
Three simulation scenarios mutate feature values to estimate risk reduction:
- **Add Resource**: Reduces `no_resource_available` and `total_blocked_events`
- **Reduce Dependencies**: Decreases dependency-related blocks and coupling overhead
- **Improve Process**: Reduces `rework_count` and `max_progress_gap`

Each task shows a before/after comparison with percentage reduction.

### Action Recommendations
Triggered rules map to prioritized actions:
- **HIGH:** Allocate additional resources
- **MEDIUM:** Review and reduce dependencies
- **LOW:** Increase monitoring frequency

### Audit-Friendly History
Every analysis is timestamped and stored with full results. Historical records include scenario type, risk breakdown, and task-level details.

---

## Frontend Design Philosophy

The UI intentionally avoids the "analytics dashboard" pattern. Rationale:

### Minimal Visuals
One donut chart (risk distribution) exists on the dashboard. Beyond that, the interface prioritizes tabular task data over decorative visualizations.

### Decision-First Hierarchy
Each page answers a decision question:
- **Dashboard:** Should I run a new analysis? What's the overall state?
- **Analysis:** Which tasks need attention? What's wrong with them?
- **History:** What did previous analyses look like?

### Single Point of Depth
The task detail panel is the only "drill-down" element. It consolidates score breakdown, explanations, actions, and what-if impact in one place.

### Accessibility and Readability
- Dark theme reduces eye strain for extended use
- Keyboard navigation (↑ ↓ Enter Esc) for power users
- Sufficient contrast ratios
- Tabular numbers for numeric alignment

### Restrained Aesthetics
Modern visual polish (gradients, glow effects, animations) is applied sparingly. The goal is professional clarity, not visual spectacle.

---

## Deterministic Behavior Explanation

This system is intentionally deterministic:

1. **Synthetic data snapshot** — The simulator runs once with a fixed seed. The resulting task/event data is static for all analyses.
2. **No runtime randomness** — Feature extraction, rule evaluation, and ML inference introduce no stochastic behavior.
3. **Reproducibility** — Running the same analysis twice produces identical results. This is essential for testing, auditing, and debugging.

The trade-off: the system cannot ingest live project data without extension. This is acceptable for a portfolio prototype; see "How This Would Scale" for production considerations.

---

## Testing Strategy

### Backend Unit Tests (`tests/`)
- **Rule evaluation:** Boundary thresholds, score capping, reason formatting
- **Feature engineering:** Aggregation correctness, missing data handling
- **Hybrid scoring:** Weight application, threshold classification
- **What-if scenarios:** Feature mutation logic
- **API endpoints:** Request/response validation, error handling

### Simulator Tests
Validate that synthetic data generation produces consistent output given identical seeds.

### Frontend Tests (Minimal)
Basic component rendering tests. The frontend is primarily validated through manual testing against the running API.

### What Is Not Tested
- ML model accuracy on real data (no real data exists)
- End-to-end browser automation
- Load testing or stress testing

---

## Limitations

This section is intentionally explicit:

| Limitation | Explanation |
|------------|-------------|
| **Synthetic data only** | All project/task data is simulated. The system has never processed real project management data. |
| **Heuristic what-if** | Scenario simulations are feature mutations, not causal models. They estimate directional impact, not precise outcomes. |
| **No persistence** | Analysis history is stored in memory. Restarting the backend clears all data. |
| **No authentication** | API key support exists but is optional. No RBAC, no user sessions. |
| **ML trained on synthetic samples** | The logistic regression model is trained on simulated data. Its coefficients reflect synthetic patterns, not real-world correlations. |
| **Demo-grade deployment** | Single-instance dev server. Not containerized. Not production-hardened. |

---

## How This Would Scale in Production

### Real Data Ingestion
- API integrations with Jira, Asana, Azure DevOps, or similar
- Streaming event ingestion via webhooks or polling
- Schema validation and data quality monitoring

### Model Retraining Pipeline
- Scheduled or triggered retraining on new labeled data
- Model versioning and A/B rollout
- Drift detection for feature distributions

### Persistence & Caching
- SQLite or PostgreSQL for analysis history
- Redis for rate limiting and session caching
- Model artifact storage (S3 or equivalent)

### RBAC & Audit Logging
- Role-based access control per project/team
- Immutable audit logs for compliance
- User-level analysis tracking

### Enterprise Deployment
- Containerized (Docker) with orchestration (Kubernetes)
- Load balancing and horizontal scaling
- Secrets management and TLS termination

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend

```bash
# From project root
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start API server
cd backend
uvicorn app:app --reload --port 8000
```

API available at `http://localhost:8000`. Swagger docs at `/docs`.

### Frontend

```bash
# From project root
cd frontend-react
npm install
npm run dev
```

UI available at `http://localhost:5173`.

### Basic Usage Flow
1. Open the frontend dashboard
2. Click "Run Analysis" to analyze synthetic project data
3. Navigate to the Analysis page to review task-level risk scores
4. Click a row to open the detail panel (explanations, actions, what-if)
5. Use the History page to review past analyses

---

## Learning Outcomes

This project demonstrates:

### System Design
- End-to-end architecture from data simulation to user interface
- Separation of concerns across modules (pipeline, models, engine, API, UI)
- Explicit trade-off decisions documented and justified

### AI Engineering
- Hybrid ML + rules approach with weighted combination
- Explainability as a first-order requirement, not an afterthought
- Feature engineering derived from domain reasoning

### Decision Intelligence
- Distinction between "analytics" and "decision support"
- What-if simulation as a decision-making tool
- Action recommendations tied to risk signals

### Production Awareness
- API design with authentication, rate limiting, metrics
- Error handling and edge case coverage
- Testing strategy proportional to project scope

### How It Differs From Typical ML Demos
Most portfolio projects train a model, report accuracy, and stop. This project:
- Integrates ML into a larger system with explicit roles
- Prioritizes explainability over marginal accuracy gains
- Includes a complete user-facing interface
- Documents limitations honestly
- Designs for auditability and determinism

---

*Project-3 in a learning progression focused on system-level AI engineering.*
