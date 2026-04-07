import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ETHERSCAN_API_KEY")

BASE_URL = "https://api.etherscan.io/v2/api"


def get_transactions(wallet_address, max_pages=2):
    all_txs = []

    for page in range(1, max_pages + 1):
        params = {
            "module": "account",
            "action": "txlist",
            "address": wallet_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": 100,
            "sort": "desc",
            "chainid": 1,
            "apikey": API_KEY
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if data.get("status") != "1":
                return []

            txs = data.get("result", [])

            if not txs:
                break

            all_txs.extend(txs)

        except Exception as e:
            print("Error:", e)
            return []

    return all_txs

if __name__ == "__main__":
    wallet = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    txs = get_transactions(wallet)
    
    print(f"Total Transactions: {len(txs)}")
    print(txs[:2])