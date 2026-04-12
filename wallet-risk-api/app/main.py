import logging
import time
from fastapi import FastAPI, HTTPException
from datetime import datetime

from schemas.risk_schema import WalletRequest
from services.cache_service import get_cached, set_cache
from services.risk_service import assess_wallet_risk
from services.data_service import fetch_wallet_data
from services.feature_service import build_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "running"}


@app.get("/health")
async def health():
    return {"status": "success"}


@app.post("/risk/score")
async def score_wallet(request: WalletRequest):

    start_time = time.time()
    wallet = request.wallet

    try:
        logger.info(f"[START] Wallet: {wallet}")

        #CACHE CHECK

        cached = get_cached(wallet)
        if cached:
            logger.info(f"[CACHE HIT] {wallet}")
            return cached

        #FETCH DATA (ASYNC)

        fetch_start = time.time()
        transactions = await fetch_wallet_data(wallet)
        print("API TX COUNT:", len(transactions))
        print("SAMPLE TX:", transactions[:1] if transactions else "EMPTY")
        logger.info(f"[DATA] {len(transactions)} txns | {time.time() - fetch_start:.2f}s")

        #FEATURE EXTRACTION

        feature_start = time.time()
        features = build_features(transactions)
        logger.info(f"[FEATURES] {features}")

        #RISK SCORING

        model_start = time.time()
        result = assess_wallet_risk(wallet, features)
        logger.info(f"[MODEL] {result}")

        #TIMEOUT FAILSAFE

        execution_time = time.time() - start_time

        if not transactions:
          logger.warning("[FALLBACK] No transactions fetched")

          return {
               "status": "partial",
               "data": {
                   "wallet": wallet,
                   "risk_level": "0.0",
                   "confidence": 0.75,
                   "reason": "EMPTY WALLET No transactions found",
                   "source": "data_unavailable"
                }
           }

        #FINAL RESPONSE

        response = {
            "status": "success",
            "data": {
                "wallet": wallet,
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "confidence": result["confidence"],
                "features": features,
                "explanation": result["explanation"],
                "source": result["source"],
                "model_version": "v1",
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Hybrid (Rules + ML + Intelligence Layer)"
            }
        }

        #STORING CACHE 

        #set_cache(wallet, response)

        return response

    except Exception as e:
        logger.error(f"[ERROR] {wallet} | {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        logger.info(f"[END] {wallet} | {time.time() - start_time:.2f}s")
