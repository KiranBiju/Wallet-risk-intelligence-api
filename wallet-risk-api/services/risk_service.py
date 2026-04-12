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

    if features["high_risk_ratio"] > 0.6:
        return {
        "wallet": wallet,
        "risk_score": 0.9,
        "risk_level": "HIGH",
        "confidence": 0.95,
        "explanation": "High proportion of risky interactions",
        "source": "rule_engine"
    }

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

def features_to_text(features):
    
    tx_frequency = features.get('tx_frequency', 0)
    avg_tx_value = features.get('avg_tx_value', 0)
    unique_interactions = features.get('unique_interactions', 0)
    contract_calls = features.get('contract_calls', 0)
    high_risk_interactions = features.get('high_risk_interactions', 0)

    
    HIGH_TX = 100
    MED_TX = 30

    HIGH_VALUE = 10
    MED_VALUE = 1

    HIGH_UNIQUE = 50
    MED_UNIQUE = 10

    HIGH_CONTRACT = 50
    MED_CONTRACT = 10

    HIGH_RISK = 10

    
    if tx_frequency > HIGH_TX:
        freq_desc = "high transaction frequency (bot-like behavior)"
    elif tx_frequency > MED_TX:
        freq_desc = "moderate transaction activity"
    else:
        freq_desc = "low transaction activity"

    
    if avg_tx_value > HIGH_VALUE:
        value_desc = "large transaction values (high-value transfers)"
    elif avg_tx_value > MED_VALUE:
        value_desc = "moderate transaction values"
    else:
        value_desc = "small transaction values"

    
    if unique_interactions > HIGH_UNIQUE:
        interaction_desc = "Many unique addresses interaction (broad network activity)"
    elif unique_interactions > MED_UNIQUE:
        interaction_desc = "interacts with a moderate number of addresses"
    else:
        interaction_desc = "limited interaction with few addresses"

    
    if contract_calls > HIGH_CONTRACT:
        contract_desc = "frequent smart contract calls (complex or automated behavior)"
    elif contract_calls > MED_CONTRACT:
        contract_desc = "moderate smart contract usage"
    else:
        contract_desc = "minimal smart contract interaction"

    
    if high_risk_interactions > HIGH_RISK:
        risk_desc = "multiple high-risk and suspicious interactions (potential fraud, exploit, or attack patterns)"
        overall = "overall behavior appears highly suspicious"
    elif high_risk_interactions > 0:
        risk_desc = "some risky and potentially suspicious interactions"
        overall = "overall behavior shows signs of possible anomaly"
    else:
        risk_desc = "no significant suspicious interactions detected"
        overall = "overall behavior appears normal"

    
    return (
        f"Transaction Behavior: {freq_desc}. "
        f"Value Pattern: {value_desc}. "
        f"Interaction Pattern: {interaction_desc}. "
        f"Contract Usage: {contract_desc}. "
        f"Risk Signals: {risk_desc}. "
        f"Overall Assessment: {overall}."
    )