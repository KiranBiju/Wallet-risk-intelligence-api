from collections import defaultdict

def build_features(transactions):

    if not transactions:
        return {
            "tx_frequency": 0,
            "avg_tx_value": 0,
            "unique_interactions": 0,
            "contract_calls": 0,
            "high_risk_interactions": 0,
            "high_risk_ratio": 0
        }

    tx_frequency = len(transactions)

    total_value = 0
    unique_addresses = set()
    contract_calls = 0
    high_risk_interactions = 0

    for tx in transactions:
        try:
            value = int(tx.get("value", 0)) / 1e18
            total_value += value

            from_addr = tx.get("from")
            to_addr = tx.get("to")

            if to_addr:
                unique_addresses.add(to_addr)

            # -----------------------------
            # CONTRACT CALL DETECTION
            # -----------------------------
            if tx.get("input") and tx["input"] != "0x":
                contract_calls += 1

            # -----------------------------
            # HIGH RISK PATTERNS
            # -----------------------------

            # 1. Very low value spam tx
            if value < 0.0001:
                high_risk_interactions += 1

            # 2. Self transactions
            if from_addr == to_addr:
                high_risk_interactions += 1

            # 3. Contract-heavy behavior
            if tx.get("input") != "0x":
                high_risk_interactions += 1

        except Exception:
            continue

    avg_tx_value = total_value / tx_frequency if tx_frequency else 0

    # -----------------------------
    # NEW: NORMALIZED FEATURE
    # -----------------------------
    high_risk_ratio = high_risk_interactions / tx_frequency

    return {
        "tx_frequency": tx_frequency,
        "avg_tx_value": avg_tx_value,
        "unique_interactions": len(unique_addresses),
        "contract_calls": contract_calls,
        "high_risk_interactions": high_risk_interactions,
        "high_risk_ratio": round(high_risk_ratio, 2)
    }