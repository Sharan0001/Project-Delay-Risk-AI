from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel
from models.hybrid_risk import hybrid_risk_score


def quick_system_test():
    # Build data
    tasks, events, features = build_raw_tables()

    # Train model
    model = DelayRiskModel()
    model.train(features)

    print("\n========== SYSTEM RISK OUTPUT ==========\n")

    for _, row in features.iterrows():
        prob = model.predict_proba(features.loc[[_]])[0]
        risk = hybrid_risk_score(row, prob)

        print(f"Task ID: {row['task_id']}")
        print(f"Delay Probability: {risk['ml_probability']}")
        print(f"Risk Score: {risk['risk_score']}")
        print(f"Risk Level: {risk['risk_level']}")

        if risk["reasons"]:
            print("Reasons:")
            for r in risk["reasons"]:
                print(f" - {r}")
        else:
            print("Reasons: None")

        print("-" * 40)


if __name__ == "__main__":
    quick_system_test()
