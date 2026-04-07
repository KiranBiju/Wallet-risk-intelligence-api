from services.model_service import predict_risk


def assess_wallet_risk(wallet, features):
    #No transactions
    
    if features["tx_frequency"] == 0:
        return {
            "wallet": wallet,
            "risk_level": "LOW",
            "confidence": 1.0,
            "reason": "No transaction history",
            "source": "rule_engine"
        }

    #RULE ENGINE

    if features["high_risk_interactions"] >= 5:
        return {
            "wallet": wallet,
            "risk_level": "HIGH",
            "confidence": 0.95,
            "reason": "Multiple high-risk interactions detected",
            "source": "rule_engine"
        }

    if features["avg_tx_value"] > 10:
        return {
            "wallet": wallet,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "reason": "Unusually high average transaction value",
            "source": "rule_engine"
        }

    
    ml = predict_risk(features)

    prob = ml["confidence"]
    pred = ml["prediction"]

    #LOW CONFIDENCE SAFETY

    if prob < 0.55:
        return {
            "wallet": wallet,
            "risk_level": "UNCERTAIN",
            "confidence": round(prob, 2),
            "reason": "Low confidence ML prediction",
            "source": "ml_model"
        }

    if prob > 0.75:
        risk = "HIGH"
    elif prob > 0.5:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    reasons = []

    if features["high_risk_interactions"] > 3:
        reasons.append("Multiple high-value suspicious transactions")

    if features["avg_tx_value"] > 5:
        reasons.append("High average transaction value")

    if not reasons:
        reasons.append("Pattern detected via ML model")


    return {
        "wallet": wallet,
        "risk_level": risk,
        "confidence": round(prob, 2),
        "reason": ", ".join(reasons),
        "source": "ml_model"
    }