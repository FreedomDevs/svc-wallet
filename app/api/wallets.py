from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional
from app.responses import success_response, error_response
from app.codes import Codes
from app.db.models import Wallet, WalletOperation
from app.db.session import get_db
from app.core.utils import TraceContext
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.api.schemas import CreateWalletRequest, DepositRequest, WithdrawRequest
from app.core.config import settings
import httpx


router = APIRouter(prefix="/wallets", tags=["wallets"])


async def verify_user_exists(user_id: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SVC_USERS_URL}/users/{user_id}", timeout=5.0)
            return response.status_code == 200
    except Exception as exc:
        return False


@router.post("")
async def create_wallet_endpoint(request: Request, payload: CreateWalletRequest, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    user_id = payload.userId
    if not await verify_user_exists(user_id):
        return error_response(
            status_code=404,
            message=f"User with id {user_id} not found",
            code=Codes.USER_NOT_FOUND
        )
    result = await db.execute(select(Wallet).where(Wallet.userId == user_id))
    if result.scalar_one_or_none():
        return error_response(
            status_code=409,
            message=f"Wallet for user {user_id} already exists",
            code=Codes.WALLET_ALREADY_EXISTS
        )
    wallet_id = str(uuid4())
    wallet = Wallet(id=wallet_id, userId=user_id)
    db.add(wallet)
    try:
        await db.commit()
        await db.refresh(wallet)
        # Подсчёт баланса через SQL SUM
        from sqlalchemy import func
        op_result = await db.execute(
            select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
        )
        balance = op_result.scalar_one()
        return success_response(
            message="Wallet successfully created",
            code=Codes.WALLET_CREATED,
            data={"id": wallet.id, "userId": wallet.userId, "balance": balance},
            status_code=201
        )
    except IntegrityError:
        await db.rollback()
        return error_response(
            status_code=409,
            message=f"Wallet for user {user_id} already exists",
            code=Codes.WALLET_ALREADY_EXISTS
        )
    except Exception as e:
        await db.rollback()
        return error_response(
            status_code=500,
            message=f"Failed to create wallet: {str(e)}",
            code=Codes.WALLET_INTERNAL_ERROR
        )

@router.get("/{userId}")
async def get_wallet_endpoint(request: Request, userId: str, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    if not await verify_user_exists(userId):
        return error_response(
            status_code=404,
            message=f"User with id {userId} not found",
            code=Codes.USER_NOT_FOUND
        )
    result = await db.execute(select(Wallet).where(Wallet.userId == userId))
    wallet = result.scalar_one_or_none()
    if not wallet:
        return error_response(
            status_code=404,
            message=f"Wallet for user {userId} not found",
            code=Codes.WALLET_NOT_FOUND
        )
    from sqlalchemy import func
    op_result = await db.execute(
        select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
    )
    balance = op_result.scalar_one()
    return success_response(
        message="Wallet fetched successfully",
        code=Codes.WALLET_FETCHED_OK,
        data={"id": wallet.id, "userId": wallet.userId, "balance": balance}
    )

@router.post("/{userId}/deposit")
async def deposit_endpoint(request: Request, userId: str, payload: DepositRequest, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    amount = payload.amount
    external_id = payload.externalOperationId
    reason = payload.reason
    if amount <= 0:
        return error_response(
            status_code=400,
            message="Amount must be greater than 0",
            code=Codes.INVALID_REQUEST
        )
    if not await verify_user_exists(userId):
        return error_response(
            status_code=404,
            message=f"User with id {userId} not found",
            code=Codes.USER_NOT_FOUND
        )
    result = await db.execute(select(Wallet).where(Wallet.userId == userId))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet_id = str(uuid4())
        wallet = Wallet(id=wallet_id, userId=userId)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    # идемпотентность
    op_result = await db.execute(select(WalletOperation).where(WalletOperation.externalOperationId == external_id))
    if op_result.scalar_one_or_none():
        return error_response(
            status_code=409,
            message="Duplicate operation",
            code=Codes.WALLET_OPERATION_DUPLICATE
        )
    # создать операцию
    from app.core.utils import get_timestamp
    operation = WalletOperation(
        id=str(uuid4()),
        walletId=wallet.id,
        amount=amount,
        type="DEPOSIT",
        reason=reason,
        externalOperationId=external_id,
        traceId=trace_id or "",
        createdAt=get_timestamp()
    )
    db.add(operation)
    await db.commit()
    # пересчитать баланс через SQL SUM
    from sqlalchemy import func
    op_result = await db.execute(
        select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
    )
    balance = op_result.scalar_one()
    return success_response(
        message="Deposit successful",
        code=Codes.WALLET_DEPOSIT_OK,
        data={"id": wallet.id, "userId": wallet.userId, "balance": balance}
    )

@router.post("/{userId}/withdraw")
async def withdraw_endpoint(request: Request, userId: str, payload: WithdrawRequest, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    amount = payload.amount
    external_id = payload.externalOperationId
    reason = payload.reason
    if amount <= 0:
        return error_response(
            status_code=400,
            message="Amount must be greater than 0",
            code=Codes.INVALID_REQUEST
        )
    if not await verify_user_exists(userId):
        return error_response(
            status_code=404,
            message=f"User with id {userId} not found",
            code=Codes.USER_NOT_FOUND
        )
    result = await db.execute(select(Wallet).where(Wallet.userId == userId))
    wallet = result.scalar_one_or_none()
    if not wallet:
        return error_response(
            status_code=404,
            message=f"Wallet for user {userId} not found",
            code=Codes.WALLET_NOT_FOUND
        )
    # идемпотентность
    op_result = await db.execute(select(WalletOperation).where(WalletOperation.externalOperationId == external_id))
    if op_result.scalar_one_or_none():
        return error_response(
            status_code=409,
            message="Duplicate operation",
            code=Codes.WALLET_OPERATION_DUPLICATE
        )
    # пересчитать баланс через SQL SUM
    from sqlalchemy import func
    op_result = await db.execute(
        select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
    )
    balance = op_result.scalar_one()
    if balance < amount:
        return error_response(
            status_code=400,
            message=f"Insufficient funds. Current balance: {balance}",
            code=Codes.WALLET_INSUFFICIENT_FUNDS
        )
    # создать операцию
    from app.core.utils import get_timestamp
    operation = WalletOperation(
        id=str(uuid4()),
        walletId=wallet.id,
        amount=-amount,
        type="WITHDRAW",
        reason=reason,
        externalOperationId=external_id,
        traceId=trace_id or "",
        createdAt=get_timestamp()
    )
    db.add(operation)
    await db.commit()
    # пересчитать баланс после операции
    op_result = await db.execute(
        select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
    )
    balance = op_result.scalar_one()
    return success_response(
        message="Withdrawal successful",
        code=Codes.WALLET_WITHDRAW_OK,
        data={"id": wallet.id, "userId": wallet.userId, "balance": balance}
    )

@router.delete("/{userId}")
async def delete_wallet_endpoint(request: Request, userId: str, db: AsyncSession = Depends(get_db)):
    trace_id = request.headers.get("X-Trace-Id")
    TraceContext.set_trace_id(trace_id)
    if not await verify_user_exists(userId):
        return error_response(
            status_code=404,
            message=f"User with id {userId} not found",
            code=Codes.USER_NOT_FOUND
        )
    result = await db.execute(select(Wallet).where(Wallet.userId == userId))
    wallet = result.scalar_one_or_none()
    if not wallet:
        return error_response(
            status_code=404,
            message=f"Wallet for user {userId} not found",
            code=Codes.WALLET_NOT_FOUND
        )
    # Проверить баланс через SQL SUM
    from sqlalchemy import func
    op_result = await db.execute(
        select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet.id)
    )
    balance = op_result.scalar_one()
    if balance != 0:
        return error_response(
            status_code=409,
            message=f"Wallet is not empty. Current balance: {balance}",
            code=Codes.WALLET_NOT_EMPTY
        )
    await db.delete(wallet)
    await db.commit()
    return success_response(
        message="Wallet deleted successfully",
        code=Codes.WALLET_DELETED,
        data=None
    )
