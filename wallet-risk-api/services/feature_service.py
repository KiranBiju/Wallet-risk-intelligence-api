def extract_features(transactions):
    if not transactions:
        return {
            "tx_frequency": 0,
            "avg_tx_value": 0,
            "unique_interactions": 0,
            "high_risk_interactions": 0
        }

    tx_frequency = len(transactions)

    values = []
    unique_addresses = set()
    high_risk_count = 0

    
    #Wei → ETH
    for tx in transactions:
        value_wei = int(tx.get("value", 0))
        value_eth = value_wei / 1e18
        values.append(value_eth)

        #Track unique interactions
        to_addr = tx.get("to")
        if to_addr:
            unique_addresses.add(to_addr.lower())

        if value_eth > 10:  # large transfer
            high_risk_count += 1

    avg_tx_value = sum(values) / len(values) if values else 0

    return {
        "tx_frequency": tx_frequency,
        "avg_tx_value": round(avg_tx_value, 6),
        "unique_interactions": len(unique_addresses),
        "high_risk_interactions": high_risk_count
    }