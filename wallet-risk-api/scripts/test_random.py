#TEST WITH RANDOM DATA TO CHECK ML EFFICIENCY
import random
from services.risk_service import assess_wallet_risk

def generate_random_features():
    return {
        "tx_frequency": random.randint(0, 500),
        "avg_tx_value": round(random.uniform(0, 20), 2),
        "unique_interactions": random.randint(0, 200),
        "contract_calls": random.randint(0, 100),
        "high_risk_interactions": random.randint(0, 10)
    }


for i in range(10):
    wallet = f"0xTEST{i}"

    features = generate_random_features()

    result = assess_wallet_risk(wallet, features)

    print("\n--- TEST", i, "---")
    print("Input:", features)
    print("Output:", result)