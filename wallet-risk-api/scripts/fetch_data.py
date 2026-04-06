import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ETHERSCAN_API_KEY")

BASE_URL = "https://api.etherscan.io/v2/api"


def get_transactions(wallet_address):
    url = BASE_URL
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "chainid": 1,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("FULL RESPONSE:", data)
    if data["status"] != "1":
        print("ERROR:", data["message"], data["result"])
        return []

    return data["result"]

if __name__ == "__main__":
    wallet = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    txs = get_transactions(wallet)
    
    print(f"Total Transactions: {len(txs)}")
    print(txs[:2])