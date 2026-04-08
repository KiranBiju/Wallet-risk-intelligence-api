import logging
import logging.config
import time
from fastapi import FastAPI, HTTPException
from schemas.risk_schema import WalletRequest
from services.risk_service import assess_wallet_risk

# setup loggers
logging.basicConfig(level=logging.INFO)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():

    logger.info("logging from the root logger")

    return {"status": "running"}

@app.get("/health")
def health():
    return{"status": "success"}

@app.post("/risk/score")
async def score_wallet(request: WalletRequest):

    start_time = time.time() 
    
    try:
        wallet = request.wallet

        logger.info(f"Received wallet: {wallet}")
        logger.info("Starting wallet risk assessment")

        features = {
        "tx_frequency": 10,
        "avg_tx_value": 2
    }
        result = assess_wallet_risk(wallet, features)

        logger.info("Risk assessment completed successfully")

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:

        logger.error(f"Error processing wallet: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(f"Execution time: {execution_time:.2f} seconds")


        

    
