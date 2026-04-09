import requests
import os

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

BASE_URL = "https://api.etherscan.io/v2/api"


def get_transactions(wallet):

    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }

    try:
        res = requests.get(BASE_URL, params=params, timeout=5)
        data = res.json()

        if data["status"] != "1":
            return []

        return data["result"]

    except Exception as e:
        print("[ETHERSCAN ERROR]", e)
        return []