"""
Machine Learning Models for Delay Risk Prediction.

Provides interpretable ML models for estimating delay probability:
- DelayRiskModel: Logistic Regression (linear, interpretable coefficients)
- DelayRiskRFModel: Random Forest (non-linear, feature importance)

Design Philosophy:
- Both models implement the same interface for interchangeability
- Feature importance is available from both for explainability
- Models are secondary to rule-based reasoning in the hybrid system
- Model persistence allows reuse without retraining
"""

import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split


# Feature columns used by all models
# These must match the output of the feature engineering pipeline
FEATURE_COLS: List[str] = [
    "total_blocked_events",
    "dependencies",
    "no_resource_available",
    "external_block",
    "random_disruption",
    "rework_count",
    "max_progress_gap",
]


class DelayRiskModel:
    """
    Logistic Regression model for delay risk prediction.
    
    Advantages:
    - Linear relationship between features and log-odds
    - Coefficients are directly interpretable
    - Fast training and prediction
    
    The model uses standardization to normalize feature scales.
    """

    def __init__(self) -> None:
        """Initialize the model pipeline with scaler and logistic regression."""
        self.pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000))
            ]
        )
        self._is_trained: bool = False

    def train(self, df: pd.DataFrame) -> None:
        """
        Train the model on labeled feature data.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target column
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        self.pipeline.fit(X, y)
        self._is_trained = True

    def train_with_validation(
        self, 
        df: pd.DataFrame, 
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Trains model with holdout validation set.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target
            test_size: Fraction of data for validation (default 0.2)
            random_state: Random seed for reproducibility
        
        Returns:
            Dictionary with validation metrics
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        self.pipeline.fit(X_train, y_train)
        self._is_trained = True
        
        # Evaluate on test set
        return self._evaluate(X_test, y_test)

    def predict_proba(self, df: pd.DataFrame) -> List[float]:
        """
        Predict delay probability for each row.
        
        Args:
            df: DataFrame with FEATURE_COLS
            
        Returns:
            List of probabilities (probability of delay)
        """
        X = df[FEATURE_COLS]
        return self.pipeline.predict_proba(X)[:, 1]

    def predict(self, df: pd.DataFrame) -> List[int]:
        """
        Predict delay class (0 or 1) for each row.
        
        Args:
            df: DataFrame with FEATURE_COLS
            
        Returns:
            List of predictions (0 = no delay, 1 = delay)
        """
        X = df[FEATURE_COLS]
        return self.pipeline.predict(X)

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Returns feature coefficients for explainability.
        
        Positive coefficients indicate features that increase delay risk.
        Negative coefficients indicate features that decrease delay risk.
        Magnitude indicates strength of relationship.
        
        Returns:
            Dictionary mapping feature names to coefficients
        """
        model = self.pipeline.named_steps["model"]
        return dict(zip(FEATURE_COLS, model.coef_[0]))

    def evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate model performance on a dataset.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target
            
        Returns:
            Dictionary with classification report and ROC-AUC score
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        return self._evaluate(X, y)

    def _evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Internal evaluation helper."""
        preds = self.pipeline.predict(X)
        probs = self.pipeline.predict_proba(X)[:, 1]
        
        # Handle case where only one class is present
        try:
            roc = roc_auc_score(y, probs)
        except ValueError:
            roc = None
        
        return {
            "accuracy": accuracy_score(y, preds),
            "classification_report": classification_report(y, preds, zero_division=0),
            "roc_auc": roc,
            "n_samples": len(y),
            "n_positive": int(y.sum()),
            "n_negative": int(len(y) - y.sum())
        }

    def save(self, path: Path) -> None:
        """
        Save trained model to disk.
        
        Args:
            path: Path to save the model (should end in .pkl or .joblib)
        """
        if not self._is_trained:
            raise ValueError("Cannot save untrained model")
        joblib.dump(self.pipeline, path)

    def load(self, path: Path) -> None:
        """
        Load pretrained model from disk.
        
        Args:
            path: Path to the saved model file
        """
        self.pipeline = joblib.load(path)
        self._is_trained = True

    @classmethod
    def from_file(cls, path: Path) -> "DelayRiskModel":
        """
        Factory method to create model from saved file.
        
        Args:
            path: Path to the saved model file
            
        Returns:
            Loaded DelayRiskModel instance
        """
        model = cls()
        model.load(path)
        return model

    @property
    def is_trained(self) -> bool:
        """Returns True if model has been trained."""
        return self._is_trained


class DelayRiskRFModel:
    """
    Random Forest model for delay risk prediction.
    
    Advantages:
    - Can capture non-linear relationships
    - Robust to outliers
    - Feature importance based on impurity reduction
    
    Disadvantages:
    - Less interpretable than logistic regression
    - Feature importance is relative, not directional
    """
    
    def __init__(self) -> None:
        """Initialize Random Forest with controlled complexity."""
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=6,
            random_state=42,
            n_jobs=-1  # Use all available cores
        )
        self._is_trained: bool = False

    def train(self, df: pd.DataFrame) -> None:
        """
        Train the model on labeled feature data.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target column
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        self.model.fit(X, y)
        self._is_trained = True

    def train_with_validation(
        self, 
        df: pd.DataFrame, 
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Trains model with holdout validation set.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target
            test_size: Fraction of data for validation (default 0.2)
            random_state: Random seed for reproducibility
        
        Returns:
            Dictionary with validation metrics
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        self._is_trained = True
        
        return self._evaluate(X_test, y_test)

    def predict_proba(self, df: pd.DataFrame) -> List[float]:
        """
        Predict delay probability for each row.
        
        Args:
            df: DataFrame with FEATURE_COLS
            
        Returns:
            List of probabilities (probability of delay)
        """
        X = df[FEATURE_COLS]
        return self.model.predict_proba(X)[:, 1]

    def predict(self, df: pd.DataFrame) -> List[int]:
        """
        Predict delay class (0 or 1) for each row.
        
        Args:
            df: DataFrame with FEATURE_COLS
            
        Returns:
            List of predictions (0 = no delay, 1 = delay)
        """
        X = df[FEATURE_COLS]
        return self.model.predict(X)

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Returns feature importance scores for explainability.
        
        For Random Forest, importance is based on mean impurity decrease.
        Higher values indicate more important features.
        Note: Values are always positive (no direction information).
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        return dict(zip(FEATURE_COLS, self.model.feature_importances_))

    def evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate model performance on a dataset.
        
        Args:
            df: DataFrame with FEATURE_COLS and 'delay' target
            
        Returns:
            Dictionary with classification report and ROC-AUC score
        """
        X = df[FEATURE_COLS]
        y = df["delay"]
        return self._evaluate(X, y)

    def _evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Internal evaluation helper."""
        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)[:, 1]
        
        try:
            roc = roc_auc_score(y, probs)
        except ValueError:
            roc = None
        
        return {
            "accuracy": accuracy_score(y, preds),
            "classification_report": classification_report(y, preds, zero_division=0),
            "roc_auc": roc,
            "n_samples": len(y),
            "n_positive": int(y.sum()),
            "n_negative": int(len(y) - y.sum())
        }

    def save(self, path: Path) -> None:
        """
        Save trained model to disk.
        
        Args:
            path: Path to save the model (should end in .pkl or .joblib)
        """
        if not self._is_trained:
            raise ValueError("Cannot save untrained model")
        joblib.dump(self.model, path)

    def load(self, path: Path) -> None:
        """
        Load pretrained model from disk.
        
        Args:
            path: Path to the saved model file
        """
        self.model = joblib.load(path)
        self._is_trained = True

    @classmethod
    def from_file(cls, path: Path) -> "DelayRiskRFModel":
        """
        Factory method to create model from saved file.
        
        Args:
            path: Path to the saved model file
            
        Returns:
            Loaded DelayRiskRFModel instance
        """
        model = cls()
        model.load(path)
        return model

    @property
    def is_trained(self) -> bool:
        """Returns True if model has been trained."""
        return self._is_trained

