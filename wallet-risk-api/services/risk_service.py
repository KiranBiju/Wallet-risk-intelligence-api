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

    # ---------------- RULE ENGINE ---------------- #

    if tx_frequency == 0:
        logger.info("[RULE] No transactions → LOW risk")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "reason": "No transactions detected",
            "explanation": "Wallet has no transaction history. No risk signals found.",
            "source": "rule_engine"
        }

    elif high_risk_ratio > 0.6:
        logger.info("[RULE] High risk interaction ratio")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.9,
            "risk_level": "HIGH",
            "confidence": 0.95,
            "reason": "High risky interaction ratio",
            "explanation": "Large proportion of transactions are flagged as high-risk.",
            "source": "rule_engine"
        }

    elif avg_tx_value > 10:
        logger.info("[RULE] High average transaction value")

        risk_result = {
            "wallet": wallet,
            "risk_score": 0.6,
            "risk_level": "MEDIUM",
            "confidence": 0.75,
            "reason": "High value transfers",
            "explanation": "Unusually high average transaction value detected.",
            "source": "rule_engine"
        }

    # ---------------- ML MODEL ---------------- #

    else:
        logger.info("[ML] Falling back to ML model")

        ml = predict_risk(features)
        prob = ml.get("confidence", 0.0)

        if prob >= 0.75:
            risk = "HIGH"
            reason = "High ML risk score"
            explanation = "Model detected strong suspicious behavioral patterns."
        elif prob >= 0.55:
            risk = "MEDIUM"
            reason = "Moderate ML risk score"
            explanation = "Model detected some unusual behavioral signals."
        else:
            risk = "LOW"
            reason = "Low ML risk score"
            explanation = "Behavior appears mostly normal based on model."

        risk_result = {
            "wallet": wallet,
            "risk_score": round(prob, 2),
            "risk_level": risk,
            "confidence": round(prob, 2),
            "reason": reason,
            "explanation": explanation,
            "source": "ml_model"
        }

    # ---------------- RAG (EXPLANATION ONLY) ---------------- #

    patterns = []

    if risk_result["risk_level"] != "LOW":
        logger.info("[RAG] Running pattern retrieval")

        try:
            feature_text = features_to_text(features)
            rag_output = retrieve_patterns(feature_text)

            patterns = rag_output if isinstance(rag_output, list) else []

        except Exception as e:
            logger.error(f"[RAG ERROR] {str(e)}")
            patterns = []

    # ---------------- ENRICH EXPLANATION ---------------- #

    risk_result["patterns_matched"] = patterns

    if patterns:
        pattern_names = [p.get("pattern", "") for p in patterns[:3]]
        pattern_summary = ", ".join(pattern_names)

        risk_result["explanation"] += f" Related patterns: {pattern_summary}."

    logger.info(f"[RESULT] {risk_result['risk_level']} risk computed")

    return risk_result


# ---------------- FEATURE → TEXT (RAG INPUT) ---------------- #

def features_to_text(features):

    tx_frequency = features.get('tx_frequency', 0)
    avg_tx_value = features.get('avg_tx_value', 0)
    unique_interactions = features.get('unique_interactions', 0)
    contract_calls = features.get('contract_calls', 0)
    high_risk_interactions = features.get('high_risk_interactions', 0)

    HIGH_TX, MED_TX = 100, 30
    HIGH_VALUE, MED_VALUE = 10, 1
    HIGH_UNIQUE, MED_UNIQUE = 50, 10
    HIGH_CONTRACT, MED_CONTRACT = 50, 10
    HIGH_RISK = 10

    freq_desc = (
        f"high freq tx ({tx_frequency})" if tx_frequency > HIGH_TX else
        f"mid freq tx ({tx_frequency})" if tx_frequency > MED_TX else
        f"low freq tx ({tx_frequency})"
    )

    value_desc = (
        f"high value ({avg_tx_value})" if avg_tx_value > HIGH_VALUE else
        f"mid value ({avg_tx_value})" if avg_tx_value > MED_VALUE else
        f"low value ({avg_tx_value})"
    )

    interaction_desc = (
        f"broad network ({unique_interactions})" if unique_interactions > HIGH_UNIQUE else
        f"moderate network ({unique_interactions})" if unique_interactions > MED_UNIQUE else
        f"limited network ({unique_interactions})"
    )

    contract_desc = (
        f"heavy contract use ({contract_calls})" if contract_calls > HIGH_CONTRACT else
        f"moderate contracts ({contract_calls})" if contract_calls > MED_CONTRACT else
        f"low contracts ({contract_calls})"
    )

    risk_desc = (
        f"high suspicious ({high_risk_interactions})" if high_risk_interactions > HIGH_RISK else
        f"some suspicious ({high_risk_interactions})" if high_risk_interactions > 0 else
        "clean"
    )

    return (
        f"tx:{freq_desc} | value:{value_desc} | "
        f"net:{interaction_desc} | contract:{contract_desc} | "
        f"risk:{risk_desc}"
    )