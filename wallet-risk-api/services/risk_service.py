from services.model_service import predict_risk
from services.explanation_service import generate_explanation


def assess_wallet_risk(wallet, features):

    #ZERO TRANSACTIONS
    
    if features["tx_frequency"] == 0:
        explanation = generate_explanation(features)

        return {
            "wallet": wallet,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "explanation": explanation,
            "source": "rule_engine"
        }

    #RULE ENGINE

    if features["high_risk_interactions"] >= 5:
        explanation = generate_explanation(features)

        return {
            "wallet": wallet,
            "risk_score": 0.9,
            "risk_level": "HIGH",
            "confidence": 0.95,
            "explanation": explanation,
            "source": "rule_engine"
        }

    if features["avg_tx_value"] > 10:
        explanation = generate_explanation(features)

        return {
            "wallet": wallet,
            "risk_score": 0.6,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "explanation": explanation,
            "source": "rule_engine"
        }

    #ML MODEL

    ml = predict_risk(features)

    prob = ml["confidence"]

    #LOW CONFIDENCE

    if prob < 0.55:
        explanation = generate_explanation(features)

        return {
            "wallet": wallet,
            "risk_score": round(prob, 2),
            "risk_level": "UNCERTAIN",
            "confidence": round(prob, 2),
            "explanation": explanation,
            "source": "ml_model"
        }

    #RISK CALCULATING
    if prob > 0.75:
        risk = "HIGH"
    elif prob > 0.5:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    #EXPLANATION PART

    explanation = generate_explanation(features)

    return {
        "wallet": wallet,
        "risk_score": round(prob, 2),
        "risk_level": risk,
        "confidence": round(prob, 2),
        "explanation": explanation,
        "source": "ml_model"
    }