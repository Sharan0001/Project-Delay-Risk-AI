from data_pipeline.build_raw_tables import build_raw_tables
from models.ml_model import DelayRiskModel, DelayRiskRFModel


def compare_models():
    _, _, features = build_raw_tables()

    lr = DelayRiskModel()
    lr.train(features)
    lr_probs = lr.predict_proba(features)

    rf = DelayRiskRFModel()
    rf.train(features)
    rf_eval = rf.evaluate(features)

    print("\n=== RANDOM FOREST EVALUATION ===")
    print(rf_eval["classification_report"])
    print("ROC-AUC:", rf_eval["roc_auc"])


if __name__ == "__main__":
    compare_models()
