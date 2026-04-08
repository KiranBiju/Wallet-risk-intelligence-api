import random
import time
from tqdm import tqdm
from scripts.fetch_data import get_transactions


def extract_connected_wallets(seed_wallet):
    txs = get_transactions(seed_wallet)

    txs = get_transactions(seed_wallet)
    print(txs[:2])

    connected = set()

    for tx in txs:
        from_addr = tx.get("from")
        to_addr = tx.get("to")

        if from_addr:
            connected.add(from_addr.lower())

        if to_addr:
            connected.add(to_addr.lower())

    return list(connected)


def crawl_wallets(seed_wallets, target_size=200):
    all_wallets = set(seed_wallets)
    queue = list(seed_wallets)

    print(f"Starting crawl with {len(seed_wallets)} seed wallets...")

    while len(all_wallets) < target_size and queue:
        current_wallet = queue.pop(0)

        try:
            new_wallets = extract_connected_wallets(current_wallet)

            for w in new_wallets:
                if w not in all_wallets:
                    all_wallets.add(w)
                    queue.append(w)

            print(f"Collected: {len(all_wallets)} wallets")

            time.sleep(0.2)

        except Exception as e:
            print(f"Error: {e}")
            continue

    return list(all_wallets)

if __name__ == "__main__":
    seed_wallet = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

    wallets = extract_connected_wallets(seed_wallet)

    print("Connected wallets:")
    print(wallets[:5])