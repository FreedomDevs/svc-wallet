from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(String, primary_key=True, index=True)
    userId = Column(String, unique=True, nullable=False, index=True)


class WalletOperation(Base):
    __tablename__ = "wallet_operations"
    id = Column(String, primary_key=True, index=True)
    walletId = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # DEPOSIT, WITHDRAW
    reason = Column(String, nullable=False)
    externalOperationId = Column(String, unique=True, nullable=False)
    traceId = Column(String, nullable=False)
    createdAt = Column(String, nullable=False)
