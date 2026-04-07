from services.risk_service import assess_wallet_risk

wallet = "0xTEST123"

features = {
    "tx_frequency": 120,
    "avg_tx_value": 4,
    "unique_interactions": 50,
    "contract_calls": 20,
    "high_risk_interactions": 2
}

result = assess_wallet_risk(wallet, features)
print(result)