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
            "chainid": 1,
            "sort": "desc",
            "apikey": API_KEY
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            #DEBUG LOG
            print("ETHERSCAN STATUS:", data.get("status"))
            print("MESSAGE:", data.get("message"))

            if data.get("status") != "1":
                print("API ERROR:", data)
                return []

            txs = data.get("result", [])

            if not txs:
                break

            all_txs.extend(txs)

        except Exception as e:
            print("FETCH ERROR:", e)
            return []

    print("FINAL TX COUNT:", len(all_txs))
    print(f"TOTAL Txn FETCHED: {len(all_txs)}")
    return all_txs

