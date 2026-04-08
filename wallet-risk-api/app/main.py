from fastapi import FastAPI
from schemas.risk_schema import WalletRequest

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return{"status": "ok"}

@app.post("/risk/score")
async def score_wallet(request: WalletRequest):
    wallet = request.wallet
    return {"wallet": wallet}    