from services.model_service import predict_risk

features = {
    "tx_frequency": 120,
    "avg_tx_value": 4,
    "unique_interactions": 50,
    "contract_calls": 20,
    "high_risk_interactions": 2
}

result = predict_risk(features)
print(result)