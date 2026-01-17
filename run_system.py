"""
Project Delay Risk AI - Command Line Interface.

This is the main entry point for running the risk analysis system
from the command line. It supports:
- Full project risk analysis
- What-if scenario exploration
- Explainable risk outputs
- Configurable simulation parameters
"""

import argparse
from typing import Optional, Dict, Any

from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel, DelayRiskRFModel
from models.hybrid_risk import hybrid_risk_score
from decision_support.explain import explain_risk
from decision_support.actions import recommend_actions
from decision_support.what_if import simulate_what_if
from backend.core.config import load_config


def run_analysis(args: argparse.Namespace) -> None:
    """
    Runs the complete risk analysis pipeline.
    
    Args:
        args: Parsed command line arguments
    """
    config = load_config()

    # Build data from simulation
    tasks, events, features = build_raw_tables(
        num_tasks=args.num_tasks,
        seed=args.seed
    )

    # Model selection based on config
    model_type = config.get("model", {}).get("type", "logistic")
    if model_type == "random_forest":
        model = DelayRiskRFModel()
    else:
        model = DelayRiskModel()
    
    # Train with validation if verbose
    if args.verbose:
        metrics = model.train_with_validation(features)
        print("\n========== MODEL TRAINING METRICS ==========")
        print(f"Model type: {model_type}")
        print(f"Training samples: {metrics['n_samples']}")
        print(f"Positive class: {metrics['n_positive']}")
        print(f"Negative class: {metrics['n_negative']}")
        print(f"Accuracy: {metrics['accuracy']:.3f}")
        if metrics['roc_auc']:
            print(f"ROC-AUC: {metrics['roc_auc']:.3f}")
        print("\n" + metrics['classification_report'])
    else:
        model.train(features)

    print("\n========== PROJECT DELAY RISK AI SYSTEM ==========")
    print(f"Analyzing {len(features)} tasks...")
    
    if args.verbose:
        weights = config.get("risk_weights", {})
        thresholds = config.get("risk_thresholds", {})
        print(f"\nConfig: rule_weight={weights.get('rule_weight', 0.6)}, "
              f"ml_weight={weights.get('ml_weight', 0.4)}")
        print(f"Thresholds: high={thresholds.get('high', 70)}, "
              f"medium={thresholds.get('medium', 40)}")
    print()

    # Count risk levels for summary
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}

    for _, row in features.iterrows():
        prob = model.predict_proba(features.loc[[_]])[0]
        
        # Pass config for configurable weights and thresholds
        risk = hybrid_risk_score(row, prob, config=config)
        risk_counts[risk["risk_level"]] += 1

        print(f"Task: {row['task_id']}")
        print(f"Risk Level: {risk['risk_level']}")
        print(f"Risk Score: {risk['risk_score']}")
        print(f"Delay Probability: {risk['ml_probability']}")
        
        if args.verbose:
            print(f"Rule Score: {risk['rule_score']}")
            print(f"Weights Used: rule={risk['weights_used']['rule_weight']}, "
                  f"ml={risk['weights_used']['ml_weight']}")

        print("\nWHY:")
        for exp in explain_risk(row, model):
            print(f" - {exp}")

        print("\nACTIONS:")
        for act in recommend_actions(row):
            print(f" - {act}")

        if args.what_if:
            simulated = simulate_what_if(row, args.what_if)
            new_prob = model.predict_proba(
                features.loc[[row.name]].assign(**simulated.to_dict())
            )[0]
            print(f"\nWHAT-IF ({args.what_if}):")
            print(f" → New delay probability ≈ {new_prob:.2f}")
            print(f" → Probability reduction: {(prob - new_prob):.2f}")

        print("-" * 60)

    # Print summary
    print("\n========== SUMMARY ==========")
    print(f"Total tasks analyzed: {len(features)}")
    print(f"High risk: {risk_counts['High']}")
    print(f"Medium risk: {risk_counts['Medium']}")
    print(f"Low risk: {risk_counts['Low']}")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI Project Delay Risk & Decision Support System"
    )

    parser.add_argument(
        "--what-if",
        type=str,
        choices=["add_resource", "reduce_dependencies", "improve_process"],
        help="Run what-if analysis with specified scenario"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including weights, metrics, and rule scores"
    )
    
    parser.add_argument(
        "--num-tasks", "-n",
        type=int,
        default=50,
        help="Number of tasks to simulate (default: 50)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for simulation (default: 42)"
    )

    args = parser.parse_args()
    run_analysis(args)


if __name__ == "__main__":
    main()
