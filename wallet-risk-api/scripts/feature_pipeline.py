import pandas as pd
from tqdm import tqdm
import time


from fetch_data import get_transactions


def extract_features(wallet):
    try:
        txs = get_transactions(wallet)

        #Skip empty wallets
        if not txs or len(txs) == 0:
            return None

        df = pd.DataFrame(txs)


        # Convert numeric fields safely
        df["value"] = pd.to_numeric(df["value"], errors='coerce') / 1e18
        df["timeStamp"] = pd.to_numeric(df["timeStamp"], errors='coerce')

        # Drop invalid rows
        df = df.dropna(subset=["value", "timeStamp"])

        # Convert timestamp to datetime
        df["timeStamp"] = pd.to_datetime(df["timeStamp"], unit='s')

        # Safety check
        if len(df) == 0:
            return None



        tx_frequency = len(df)

        avg_tx_value = df["value"].mean()

        unique_interactions = df["to"].nunique()

        contract_calls = (df["input"] != "0x").sum()

        # Basic risk heuristic (temporary)
        high_risk_interactions = df[df["value"] > 10].shape[0]

        

        # Time span (in days)
        time_span_days = (df["timeStamp"].max() - df["timeStamp"].min()).days + 1

        # Avoid division by zero
        if time_span_days == 0:
            time_span_days = 1

        tx_per_day = tx_frequency / time_span_days

        # Value volatility (important behavioral signal)
        value_std = df["value"].std()

        # Max transaction value (whale behavior)
        max_tx_value = df["value"].max()


        features = {
            "wallet": wallet,
            "tx_frequency": tx_frequency,
            "avg_tx_value": avg_tx_value,
            "unique_interactions": unique_interactions,
            "contract_calls": contract_calls,
            "high_risk_interactions": high_risk_interactions,
            "tx_per_day": tx_per_day,
            "value_std": value_std,
            "max_tx_value": max_tx_value
        }

        return features

    except Exception as e:
        print(f"Error processing wallet {wallet}: {e}")
        return None


#DATASET BUILDER


def build_dataset(wallets, output_file="wallet_dataset.csv"):
    data = []

    for wallet in tqdm(wallets):
        features = extract_features(wallet)

        if features:
            data.append(features)

        #Avoid API rate limit
        time.sleep(0.2)

    df = pd.DataFrame(data)

    #Save dataset
    df.to_csv(output_file, index=False)

    print(f"\n✅ Dataset saved as {output_file}")
    print(f"Total wallets processed: {len(df)}")

    return df



#Main function
if __name__ == "__main__":

    #Sample wallets (you can expand later)
    wallets = [
        "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    ]

    # Quick scaling (temporary trick)
    wallets = wallets * 50  # → 100 wallets

    dataset = build_dataset(wallets)