def generate_explanation(features):
    if features["tx_frequency"] > 100:
        return "High transaction frequency detected"

    if features["avg_tx_value"] > 5:
        return "Large average transaction value"

    if features["high_risk_interactions"] > 3:
        return "Multiple high-risk interactions detected"

    return "Normal transaction behavior"