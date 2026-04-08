import logging
import time
from fastapi import FastAPI, HTTPException
from datetime import datetime

from schemas.risk_schema import WalletRequest
from services.cache_service import get_cached, set_cache
from services.risk_service import assess_wallet_risk
from services.data_service import fetch_wallet_data
from services.feature_service import extract_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    logger.info("Root endpoint hit")
    return {"status": "running"}


@app.get("/health")
def health():
    return {"status": "success"}


@app.post("/risk/score")
async def score_wallet(request: WalletRequest):

    start_time = time.time()

    try:
        wallet = request.wallet
        logger.info(f"[START] Wallet received: {wallet}")

        #CACHE CHECK

        cached = get_cached(wallet)
        if cached:
            logger.info(f"[CACHE HIT] Wallet: {wallet}")
            return cached

        #FETCH DATA

        fetch_start = time.time()
        transactions = fetch_wallet_data(wallet)
        logger.info(f"[DATA] Transactions fetched: {len(transactions)} | Time: {time.time() - fetch_start:.2f}s")

        #FEATURE EXTRACTION

        feature_start = time.time()
        features = extract_features(transactions)
        logger.info(f"[FEATURES] {features} | Time: {time.time() - feature_start:.2f}s")

        #RISK SCORING

        model_start = time.time()
        result = assess_wallet_risk(wallet, features)
        logger.info(f"[MODEL] Result: {result} | Time: {time.time() - model_start:.2f}s")

        #TIMEOUT FAILSAFE

        execution_time = time.time() - start_time
        if execution_time > 5:
            logger.warning(f"[TIMEOUT] Execution exceeded 5s: {execution_time:.2f}s")

            return {
                "status": "partial",
                "data": {
                    "wallet": wallet,
                    "risk_level": "UNKNOWN",
                    "confidence": 0.5,
                    "reason": "Timeout during processing",
                    "source": "fallback_timeout"
                }
            }

        #FINAL RESPONSE

        response = {
            "status": "success",
            "data": {
                "wallet": wallet,
                "risk_score": result.get("risk_score"),
                "risk_level": result.get("risk_level"),
                "confidence": result.get("confidence"),
                "features": features,
                "explanation": result.get("explanation"),
                "source": result.get("source"),
                "model_version": "v1",
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Heuristic + ML hybrid system. Not financial advice."
            }
        }

        #CACHE STORE
        
        set_cache(wallet, response)
        logger.info(f"[CACHE SET] Wallet stored: {wallet}")

        return response

    except Exception as e:
        logger.error(f"[ERROR] Wallet: {request.wallet} | Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        total_time = time.time() - start_time
        logger.info(f"[END] Total execution time: {total_time:.2f}s")