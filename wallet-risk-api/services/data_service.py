import httpx
import logging
import os

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")


async def fetch_wallet_data(wallet: str):

    url = "https://api.etherscan.io/v2/api"

    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 100,
        "chainid":1,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)

        logger.info(f"[ETHERSCAN STATUS CODE] {response.status_code}")

        if response.status_code != 200:
            logger.error(f"[ETHERSCAN ERROR] HTTP {response.status_code}")
            return []

        data = response.json()
        print("FULL RESPONSE:", data)

        logger.info(f"[ETHERSCAN RAW] {data}")

        #ERROR HANDLING
        
        status = data.get("status")
        message = data.get("message", "")

        #SUCCESS CASE
        if status == "1":
           transactions = data.get("result", [])

           if not isinstance(transactions, list):
              logger.error("[DATA ERROR] Invalid transaction format")
              return []

           logger.info(f"[FETCH SUCCESS] {len(transactions)} transactions")
           return transactions

        #EMPTY WALLET

        if "No transactions found" in message:
            logger.info("[ETHERSCAN] No transactions found (valid case)")
            return []

        #ACTUAL ERROR

        logger.error(f"[ETHERSCAN FAILED] {data}")
        return []
        #ACTUAL ERROR
        
        logger.error(f"[ETHERSCAN FAILED] {data}")
        return []

        transactions = data.get("result", [])

        if not isinstance(transactions, list):
            logger.error("[DATA ERROR] Invalid transaction format")
            return []

        logger.info(f"[FETCH SUCCESS] {len(transactions)} transactions")

        return transactions

    except httpx.RequestError as e:
        logger.error(f"[NETWORK ERROR] {str(e)}")
        return []

    except Exception as e:
        logger.error(f"[UNKNOWN ERROR] {str(e)}", exc_info=True)
        return []