import logging
from services.model_service import predict_risk
from services.rag_service import retrieve_patterns
from services.llm_service import generate_explanation
from services.feature_service import features_to_text

logger = logging.getLogger(__name__)


def assess_wallet_risk(wallet, features):

    logger.info(f"[RISK] Starting assessment for wallet: {wallet}")

    tx_frequency = features.get("tx_frequency", 0)
    avg_tx_value = features.get("avg_tx_value", 0)
    high_risk_interactions = features.get("high_risk_interactions", 0)

    total_tx = max(tx_frequency, 1)
    high_risk_ratio = high_risk_interactions / total_tx

    

    if tx_frequency == 0:
        return {
            "wallet": wallet,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "explanation": {
                "summary": "No transaction history detected",
                "key_risk_factors": [],
                "verdict": "LOW"
            },
            "source": "rule_engine"
        }

    elif high_risk_ratio > 0.6:
        return {
            "wallet": wallet,
            "risk_score": 0.9,
            "risk_level": "HIGH",
            "confidence": 0.95,
            "explanation": {
                "summary": "High proportion of suspicious interactions",
                "key_risk_factors": ["high-risk transactions"],
                "verdict": "HIGH"
            },
            "source": "rule_engine"
        }

    elif avg_tx_value > 10:
        return {
            "wallet": wallet,
            "risk_score": 0.6,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "explanation": {
                "summary": "Unusually high transaction values",
                "key_risk_factors": ["high-value transfers"],
                "verdict": "MEDIUM"
            },
            "source": "rule_engine"
        }

    

    ml = predict_risk(features)
    prob = ml.get("confidence")

    if prob is None:
        logger.error("[ML ERROR] Missing confidence score")
        prob = 0.5

    if prob >= 0.75:
        risk_level = "HIGH"
    elif prob >= 0.55:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    logger.info(f"[ML] Risk level: {risk_level} | Prob: {prob}")

    

    if risk_level == "LOW":
        return {
            "wallet": wallet,
            "risk_score": round(prob, 2),
            "risk_level": "LOW",
            "confidence": round(prob, 2),
            "explanation": {
                "summary": "Wallet shows normal behavior with no significant anomalies",
                "key_risk_factors": [],
                "verdict": "LOW"
            },
            "source": "ml_model"
        }


    try:
        feature_text = features_to_text(features)
        patterns = retrieve_patterns(feature_text)
    except Exception as e:
        logger.error(f"[RAG ERROR] {str(e)}")
        patterns = []


    try:
        llm_output = generate_explanation(
            risk_score=prob,
            risk_level=risk_level,
            features=features,
            patterns=patterns
        )
    except Exception as e:
        logger.error(f"[LLM ERROR] {str(e)}")

        llm_output = {
            "summary": f"{risk_level} risk detected based on ML + RAG signals",
            "key_risk_factors": ["behavioral anomalies", "transaction patterns"],
            "verdict": risk_level
        }

    return {
        "wallet": wallet,
        "risk_score": round(prob, 2),
        "risk_level": risk_level,
        "confidence": round(prob, 2),
        "explanation": llm_output,
        "patterns_matched": patterns,
        "source": "ml_rag_llm"
    }