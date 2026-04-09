from services.model_service import predict_risk
from services.explanation_service import generate_explanation


def assess_wallet_risk(wallet, features):

    #ZERO TRANSACTIONS

    if features["tx_frequency"] == 0:
        return {
            "wallet": wallet,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "explanation": generate_explanation(features),
            "source": "rule_engine"
        }

    #HIGH RISK INTERACTIONS

    ratio = features["high_risk_ratio"]

    if ratio > 0.75:
       risk = "HIGH"
       score = 0.9

    elif ratio > 0.5:
         risk = "MEDIUM"
         score = 0.7

    else:
         risk = None

    #ABNORMAL VALUE

    if features["avg_tx_value"] > 10:
        return {
            "wallet": wallet,
            "risk_score": 0.6,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "explanation": generate_explanation(features),
            "source": "rule_engine"
        }

    #ML MODEL

    ml = predict_risk(features)
    prob = ml["confidence"]

    #LOW CONFIDENCE

    if prob < 0.55:
        return {
            "wallet": wallet,
            "risk_score": round(prob, 2),
            "risk_level": "UNCERTAIN",
            "confidence": round(prob, 2),
            "explanation": generate_explanation(features),
            "source": "ml_model"
        }

    #FINAL RISK CHECKING

    if prob >= 0.75:
        risk = "HIGH"
    elif prob >= 0.55:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "wallet": wallet,
        "risk_score": round(prob, 2),
        "risk_level": risk,
        "confidence": round(prob, 2),
        "explanation": generate_explanation(features),
        "source": "ml_model"
    }