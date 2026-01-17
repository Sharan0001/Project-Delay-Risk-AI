from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel


def train_delay_model():
    # Build data
    tasks, events, features = build_raw_tables()

    # Train model
    model = DelayRiskModel()
    model.train(features)

    # Inspect feature influence
    importance = model.get_feature_importance()

    print("\n--- FEATURE IMPORTANCE (LOGISTIC REGRESSION) ---")
    for k, v in sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"{k:25s} {v:.3f}")

    # Quick probability sanity check
    probs = model.predict_proba(features)

    print("\n--- SAMPLE PREDICTIONS ---")
    for task_id, prob in zip(features["task_id"], probs):
        print(f"Task {task_id}: delay probability = {prob:.2f}")

    return model, features


if __name__ == "__main__":
    train_delay_model()
