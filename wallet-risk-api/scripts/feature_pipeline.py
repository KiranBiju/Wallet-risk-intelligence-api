import pandas as pd
from tqdm import tqdm
import time

# Import modules
from fetch_data import get_transactions
from wallet_crawler import crawl_wallets

def assign_label(features):
    score = 0

    if features["tx_frequency"] > 200:
        score += 1

    if features["avg_tx_value"] > 5:
        score += 1

    if features["high_risk_interactions"] > 3:
        score += 1

    if features["contract_calls"] > 50:
        score += 1

    return 1 if score >= 2 else 0


#FEATURE EXTRACTION

def extract_features(wallet):
    try:
        txs = get_transactions(wallet)

        #Skip empty wallets
        if not txs or len(txs) == 0:
            return None

        df = pd.DataFrame(txs)

        #DATA CLEANING

        df["value"] = pd.to_numeric(df["value"], errors='coerce') / 1e18
        df["timeStamp"] = pd.to_numeric(df["timeStamp"], errors='coerce')

        df = df.dropna(subset=["value", "timeStamp"])

        df["timeStamp"] = pd.to_datetime(df["timeStamp"], unit='s')

        if len(df) == 0:
            return None

        #BASIC FEATURES

        tx_frequency = len(df)

        #Skip low-activity wallets

        if tx_frequency < 5:
            return None

        avg_tx_value = df["value"].mean()
        unique_interactions = df["to"].nunique()
        contract_calls = (df["input"] != "0x").sum()
        high_risk_interactions = df[df["value"] > 10].shape[0]

        #ADVANCED FEATURES

        time_span_days = (df["timeStamp"].max() - df["timeStamp"].min()).days + 1
        time_span_days = max(time_span_days, 1)

        tx_per_day = tx_frequency / time_span_days

        value_std = df["value"].std()
        max_tx_value = df["value"].max()

        #HANDLE EDGE CASES

        if pd.isna(value_std):
            value_std = 0

        if pd.isna(avg_tx_value):
            avg_tx_value = 0

        #FINAL FEATURE DICT
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

        #ADD LABEL
        features["label"] = assign_label(features)

        return features

    except Exception as e:
        print(f"Error processing wallet {wallet}: {e}")
        return None


#DATASET BUILDER

def build_dataset(wallets, output_file="db/wallet_dataset.csv"):
    rows = []

    for wallet in tqdm(wallets):
        try:
            print(f"Processing: {wallet}")

            start_time = time.time()

            #CALL ONLY ONCE
            features = extract_features(wallet)

            #Skip slow wallets
            if time.time() - start_time > 15:
                print(f"Skipping slow wallet: {wallet}")
                continue  

            if features:
                rows.append(features)

            time.sleep(0.2)

        except Exception as e:
            print(f"Error processing {wallet}: {e}")
            continue

    df = pd.DataFrame(rows)

    # Save dataset
    df.to_csv(output_file, index=False)

    print(f"\n Dataset saved as {output_file}")
    print(f"Total wallets processed: {len(df)}")

    if not df.empty:
        print("Unique wallets:", df["wallet"].nunique())

    return df

    #NEW: Check uniqueness
    if not df.empty:
        print("Unique wallets:", df["wallet"].nunique())

    return df


#MAIN

if __name__ == "__main__":

    #Seed wallets
    seed_wallets = [
        "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    ]

    # Crawl real wallets
    wallets = crawl_wallets(seed_wallets, target_size=200)

    print(f"Total wallets collected: {len(wallets)}")

    # Build dataset
    dataset = build_dataset(wallets)