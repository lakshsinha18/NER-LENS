"""Train and evaluate a reproducible demo baseline using synthetic, labelled samples.

The synthetic labels are clearly for prototype development only and must be
replaced by curated/verified records before operational use.
"""
from datetime import date
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
try:
    from xgboost import XGBClassifier
except Exception:  # missing native OpenMP runtime or package; keeps the demo runnable
    XGBClassifier = None

FEATURES = ["rainfall_1h", "rainfall_6h", "rainfall_24h", "rainfall_72h", "rainfall_7d", "soil_moisture", "slope", "elevation", "aspect", "historical_landslide_count", "distance_to_road", "land_cover_risk"]


def make_demo_data(samples: int = 1400) -> pd.DataFrame:
    rng = np.random.default_rng(20260828)
    x = pd.DataFrame({
        "rainfall_1h": rng.gamma(2, 10, samples), "rainfall_6h": rng.gamma(2.2, 19, samples),
        "rainfall_24h": rng.gamma(2.4, 34, samples), "rainfall_72h": rng.gamma(2.6, 58, samples),
        "rainfall_7d": rng.gamma(3, 95, samples), "soil_moisture": rng.uniform(28, 98, samples),
        "slope": rng.uniform(3, 48, samples), "elevation": rng.uniform(50, 2600, samples), "aspect": rng.uniform(0, 360, samples),
        "historical_landslide_count": rng.integers(0, 9, samples), "distance_to_road": rng.uniform(.1, 15, samples), "land_cover_risk": rng.uniform(.1, 1, samples),
    })
    pressure = x.rainfall_24h / 175 + x.soil_moisture / 155 + x.slope / 70 + x.historical_landslide_count / 15 + x.land_cover_risk / 2 - x.distance_to_road / 65 + rng.normal(0, .19, samples)
    x["target"] = (pressure > 1.62).astype(int)
    return x


def main():
    df = make_demo_data()
    x_train, x_test, y_train, y_test = train_test_split(df[FEATURES], df.target, test_size=.22, random_state=42, stratify=df.target)
    candidates = {"Random Forest baseline": RandomForestClassifier(n_estimators=180, max_depth=10, min_samples_leaf=3, class_weight="balanced", random_state=42)}
    if XGBClassifier is not None:
        candidates["XGBoost main model"] = XGBClassifier(n_estimators=180, max_depth=5, learning_rate=.055, subsample=.85, colsample_bytree=.85, eval_metric="logloss", random_state=42)
    all_metrics, trained = {}, {}
    for name, candidate in candidates.items():
        candidate.fit(x_train, y_train)
        probability = candidate.predict_proba(x_test)[:, 1]
        prediction = (probability >= .5).astype(int)
        all_metrics[name] = {"accuracy": round(accuracy_score(y_test, prediction), 3), "precision": round(precision_score(y_test, prediction, zero_division=0), 3), "recall": round(recall_score(y_test, prediction, zero_division=0), 3), "f1": round(f1_score(y_test, prediction, zero_division=0), 3), "roc_auc": round(roc_auc_score(y_test, probability), 3)}
        trained[name] = candidate
    best_name = max(all_metrics, key=lambda name: all_metrics[name]["roc_auc"])
    model, selected = trained[best_name], all_metrics[best_name]
    metrics = {**selected, "samples": len(df), "training_date": str(date.today()), "model": best_name, "comparison": all_metrics, "data_notice": "Training samples are synthetic demo data, not verified historical records."}
    output = Path(__file__).resolve().parents[1] / "ml/models"
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "landslide_model.pkl")
    (output / "metrics.json").write_text(json.dumps({**metrics, "feature_importance": dict(zip(FEATURES, [round(float(v), 4) for v in model.feature_importances_]))}, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__": main()
