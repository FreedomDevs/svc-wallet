from pydantic import BaseModel

class CreateWalletRequest(BaseModel):
    userId: str

class DepositRequest(BaseModel):
    amount: int
    externalOperationId: str
    reason: str

class WithdrawRequest(BaseModel):
    amount: int
    externalOperationId: str
    reason: str
