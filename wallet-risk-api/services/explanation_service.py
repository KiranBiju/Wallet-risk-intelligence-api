def generate_explanation(features, patterns=None):

    try:
        # MOCK LLM (Deterministic)
        if features["high_risk_ratio"] > 0.7:
            explanation = "High risk due to high proportion of risky interactions."
        elif features["tx_frequency"] > 200:
            explanation = "Unusual high transaction frequency detected."
        else:
            explanation = "Normal transaction behavior."

        if patterns:
            pattern_names = [p["pattern"] for p in patterns]
            explanation += f" Detected patterns: {', '.join(pattern_names)}"

        print("[LLM] Generated explanation")
        return explanation

    except Exception:
        return "Risk detected based on abnormal activity patterns."