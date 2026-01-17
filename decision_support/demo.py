from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel
from models.hybrid_risk import hybrid_risk_score
from decision_support.explain import explain_risk
from decision_support.actions import recommend_actions
from decision_support.what_if import simulate_what_if


def run_demo():
    # Build data
    tasks, events, features = build_raw_tables()

    # Train model
    model = DelayRiskModel()
    model.train(features)

    print("\n========== AI DECISION SUPPORT OUTPUT ==========\n")

    for _, row in features.iterrows():
        prob = model.predict_proba(features.loc[[_]])[0]
        risk = hybrid_risk_score(row, prob)

        print(f"Task: {row['task_id']}")
        print(f"Risk Level: {risk['risk_level']}")
        print(f"Risk Score: {risk['risk_score']}")
        print(f"Delay Probability: {risk['ml_probability']}")

        print("\nWHY:")
        for exp in explain_risk(row, model):
            print(f" - {exp}")

        print("\nRECOMMENDED ACTIONS:")
        for act in recommend_actions(row):
            print(f" - {act}")

        print("\nWHAT-IF (Add Resource):")
        simulated = simulate_what_if(row, "add_resource")
        new_prob = model.predict_proba(
            features.loc[[row.name]].assign(**simulated.to_dict())
        )[0]
        print(f" → Estimated delay probability drops to {new_prob:.2f}")

        print("-" * 50)


if __name__ == "__main__":
    run_demo()
