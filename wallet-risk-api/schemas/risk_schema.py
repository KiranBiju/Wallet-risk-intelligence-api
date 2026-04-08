from pydantic import BaseModel,Field

class WalletRequest(BaseModel):
    wallet: str = Field(min_length=5, max_length=45)