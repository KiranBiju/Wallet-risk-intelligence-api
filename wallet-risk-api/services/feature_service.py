from collections import defaultdict

def build_features(transactions):

    if not transactions:
        return {
            "tx_frequency": 0,
            "avg_tx_value": 0,
            "unique_interactions": 0,
            "contract_calls": 0,
            "high_risk_interactions": 0,
            "high_risk_ratio": 0.0
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

            if from_addr:
              unique_addresses.add(from_addr)
            if to_addr:
               unique_addresses.add(to_addr)

           
            is_contract = tx.get("input") and tx.get("input") != "0x"
            if is_contract:
                contract_calls += 1

        
            is_high_risk = False

            if value < 0.0001:
                is_high_risk = True

            if from_addr and to_addr and from_addr == to_addr:
                is_high_risk = True

            if is_contract and value < 0.0001:
                is_high_risk = True

            if is_high_risk:
                high_risk_interactions += 1

            error_tx = tx.get("isError") == "1"

            if error_tx:
             is_high_risk = True    

        except Exception:
            continue

    avg_tx_value = total_value / tx_frequency if tx_frequency else 0

    
    high_risk_interactions = min(high_risk_interactions, tx_frequency)

    
    high_risk_ratio = (
        high_risk_interactions / tx_frequency if tx_frequency > 0 else 0.0
    )

    
    print("FINAL FEATURES:", {
        "tx_frequency": tx_frequency,
        "high_risk_interactions": high_risk_interactions,
        "ratio": round(high_risk_ratio, 2)
    })

    return {
        "tx_frequency": tx_frequency,
        "avg_tx_value": round(avg_tx_value, 6),
        "unique_interactions": len(unique_addresses),
        "contract_calls": contract_calls,
        "high_risk_interactions": high_risk_interactions,
        "high_risk_ratio": round(high_risk_ratio, 2)
    }
    