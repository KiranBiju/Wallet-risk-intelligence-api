import logging
from services.model_service import predict_risk
from services.rag_service import retrieve_patterns

logger = logging.getLogger(__name__)


def assess_wallet_risk(wallet, features):

    logger.info(f"[RISK] Starting assessment for wallet: {wallet}")

    tx_frequency = features.get("tx_frequency", 0)
    avg_tx_value = features.get("avg_tx_value", 0)
    high_risk_interactions = features.get("high_risk_interactions", 0)

    total_tx = max(tx_frequency, 1)
    high_risk_ratio = high_risk_interactions / total_tx

    decision_path = []


    if tx_frequency == 0:
        decision_path.append("RULE: NO_TX")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "reason": "No transactions",
            "explanation": "No transactions have been made by this wallet. No risk signals detected.",
            "source": "rule_engine"
        }

    elif high_risk_ratio > 0.6:
        decision_path.append("RULE: HIGH_RISK_RATIO")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.9,
            "risk_level": "HIGH",
            "confidence": 0.95,
            "reason": "High risky interaction ratio",
            "explanation": "A large proportion of transactions are classified as risky.",
            "source": "rule_engine"
        }

    elif avg_tx_value > 10:
        decision_path.append("RULE: HIGH_VALUE")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.6,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "reason": "High value transfers",
            "explanation": "This wallet performs unusually high-value transactions.",
            "source": "rule_engine"
        }

    else:
        
        decision_path.append("ML_MODEL")

        ml = predict_risk(features)
        prob = ml.get("confidence", 0.0)

        if prob >= 0.75:
            risk = "HIGH"
            reason = "High ML risk score"
            explanation = "Model detected strong suspicious behavioral signals."
        elif prob >= 0.55:
            risk = "MEDIUM"
            reason = "Moderate ML risk score"
            explanation = "Model detected some unusual patterns."
        else:
            risk = "LOW"
            reason = "Low ML risk score"
            explanation = "Behavior appears mostly normal."

        risk_result = {
            "wallet": wallet,
            "risk_score": round(prob, 2),
            "risk_level": risk,
            "confidence": round(prob, 2),
            "reason": reason,
            "explanation": explanation,
            "source": "ml_model"
        }

    # RAG LAYER (ONLY IF NOT LOW)

    patterns = []

    if risk_result["risk_level"] != "LOW":
        decision_path.append("RAG")

        try:
            feature_text = features_to_text(features)
            rag_output = retrieve_patterns(feature_text)

            if isinstance(rag_output, list):
                patterns = rag_output
            else:
                patterns = []

            logger.info(f"[RAG] Retrieved patterns: {patterns}")

        except Exception as e:
            logger.error(f"[RAG ERROR] {str(e)}")
            patterns = []

   

    risk_result["patterns_matched"] = patterns

    if patterns:
        pattern_names = [
            p.get("pattern") 
            for p in patterns[:3] 
            if p.get("pattern")
        ]

        if pattern_names:
            pattern_summary = ", ".join(pattern_names)
            risk_result["explanation"] += f" Related patterns detected: {pattern_summary}."

    
    else:
        if risk_result["risk_level"] == "HIGH":
            risk_result["explanation"] += " High risk due to frequent suspicious interactions."
        elif risk_result["risk_level"] == "MEDIUM":
            risk_result["explanation"] += " Moderate risk due to unusual activity patterns."
        else:
            risk_result["explanation"] += " No strong scam patterns matched, but behavioral anomalies were detected."    


    risk_result["explainability"] = {
        "ml_features": features,
        "decision_path": " → ".join(decision_path),
        "pattern_count": len(patterns)
    }

    logger.info(f"[FINAL RESULT] {risk_result['risk_level']} risk")

    return risk_result


#FEATURE → TEXT (FOR RAG)

def features_to_text(features):

    tx_frequency = features.get('tx_frequency', 0)
    avg_tx_value = features.get('avg_tx_value', 0)
    unique_interactions = features.get('unique_interactions', 0)
    contract_calls = features.get('contract_calls', 0)
    high_risk_interactions = features.get('high_risk_interactions', 0)
    high_risk_ratio = features.get('high_risk_ratio', 0)

    signals = []

    if tx_frequency > 80:
        signals.append("high frequency activity")
    elif tx_frequency > 30:
        signals.append("moderate transaction activity")

    if avg_tx_value > 100:
        signals.append("large transfer anomaly")
    elif avg_tx_value > 10:
        signals.append("high value transfers")

    if unique_interactions < 5:
        signals.append("single counterparty dependency")
    elif unique_interactions > 50:
        signals.append("broad interaction network")

    if contract_calls > 50:
        signals.append("heavy contract interaction")

    if high_risk_ratio > 0.7:
        signals.append("flagged wallet interaction")
        signals.append("fund drain pattern")
    elif high_risk_ratio > 0.3:
        signals.append("suspicious interaction pattern")

    if not signals:
        signals.append("normal wallet behavior")

    return " | ".join(signals)