import joblib
import numpy as np
import pandas as pd

FEATURES = [
    "tx_frequency",
    "avg_tx_value",
    "unique_interactions",
    "contract_calls",
    "high_risk_interactions"
]

# LOAD VERSIONED ARTIFACTS
model = joblib.load("ml/risk_model_v1.pkl")
scaler = joblib.load("ml/scaler_v1.pkl")


def predict_risk(features):

    try:
        
        X = pd.DataFrame([features], columns=FEATURES)
        
        X_scaled = scaler.transform(X)

    
        prob = model.predict_proba(X_scaled)[0][1]
        pred = model.predict(X_scaled)[0]

        confidence = float(prob)

        #LOGGING

        print(f"[ML] Prediction={pred}, Prob={prob:.4f}")

        return {
            "prediction": int(pred),
            "probability": float(prob),
            "confidence": float(confidence)
        }

    except Exception as e:
        print("[ML ERROR]", e)
        return {
            "prediction": 0,
            "probability": 0.0,
            "confidence": 0.5
        }