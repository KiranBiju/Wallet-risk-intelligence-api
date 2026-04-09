from collections import defaultdict

def build_features(transactions):

    if not transactions:
        return {
            "tx_frequency": 0,
            "avg_tx_value": 0,
            "unique_interactions": 0,
            "contract_calls": 0,
            "high_risk_interactions": 0
        }

    tx_count = len(transactions)

    total_value = 0
    unique_addresses = set()
    contract_calls = 0
    high_risk = 0

    for tx in transactions:

        value = int(tx["value"]) / 1e18  # ETH
        total_value += value

        unique_addresses.add(tx["to"])

        #CONTRACT INTERACTION
        if tx["input"] != "0x":
            contract_calls += 1

        if value < 0.01:
            high_risk += 1

    return {
        "tx_frequency": tx_count,
        "avg_tx_value": total_value / tx_count,
        "unique_interactions": len(unique_addresses),
        "contract_calls": contract_calls,
        "high_risk_interactions": high_risk
    }