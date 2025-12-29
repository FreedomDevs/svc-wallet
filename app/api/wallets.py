import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional
from app.responses import success_response, error_response
from app.codes import Codes
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import CreateWalletRequest, DepositRequest, WithdrawRequest
from app.service.wallet_service import WalletService
from app.repository.wallet_repository import WalletRepository
from app.core.config import settings
import httpx


router = APIRouter(prefix="/wallets", tags=["wallets"])


async def verify_user_exists(user_id: str) -> bool:
    """
    Проверяет существование пользователя по user_id через внешний сервис пользователей.
    Возвращает True, если пользователь найден, иначе False.
    Логирует ошибку при сбое запроса.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SVC_USERS_URL}/users/{user_id}", timeout=5.0)
            return response.status_code == 200
    except (httpx.RequestError, httpx.TimeoutException, httpx.ConnectError) as exc:
        logging.exception(
            f"[{datetime.utcnow().isoformat()}] Error verifying user existence: user_id={user_id}, endpoint={endpoint}, trace_id={trace_id}, exc={str(exc)}"
        )
        return False


@router.post("")
async def create_wallet_endpoint(request: Request, payload: CreateWalletRequest, db: AsyncSession = Depends(get_db)):
    """
    Создать кошелёк для пользователя. Возвращает ошибку, если пользователь не найден или кошелёк уже существует.
    """
    trace_id = getattr(request.state, 'trace_id', None)
    repository = WalletRepository(db)
    service = WalletService(repository, verify_user_exists)
    data, code = await service.create_wallet(payload.userId)
    if code == Codes.USER_NOT_FOUND:
        return error_response(status_code=404, message=f"User with id {payload.userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_ALREADY_EXISTS:
        return error_response(status_code=409, message=f"Wallet for user {payload.userId} already exists", code=code, trace_id=trace_id)
    if code == Codes.WALLET_CREATED:
        return success_response(message="Wallet successfully created", code=code, data=data, status_code=201, trace_id=trace_id)
    return error_response(status_code=500, message="Failed to create wallet", code=Codes.WALLET_INTERNAL_ERROR, trace_id=trace_id)


@router.get("/{userId}")
async def get_wallet_endpoint(request: Request, userId: str, db: AsyncSession = Depends(get_db)):
    """
    Получить информацию о кошельке пользователя по userId.
    Возвращает ошибку, если пользователь или кошелёк не найден.
    """
    trace_id = getattr(request.state, 'trace_id', None)
    repository = WalletRepository(db)
    service = WalletService(repository, verify_user_exists)
    data, code = await service.get_wallet(userId)
    if code == Codes.USER_NOT_FOUND:
        return error_response(status_code=404, message=f"User with id {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_NOT_FOUND:
        return error_response(status_code=404, message=f"Wallet for user {userId} not found", code=code, trace_id=trace_id)
    return success_response(message="Wallet fetched successfully", code=code, data=data, trace_id=trace_id)


@router.post("/{userId}/deposit")
async def deposit_endpoint(request: Request, userId: str, payload: DepositRequest, db: AsyncSession = Depends(get_db)):
    """
    Пополнить баланс кошелька пользователя.
    Проверяет корректность суммы, существование пользователя и дублирование операции.
    """
    trace_id = getattr(request.state, 'trace_id', None)
    repository = WalletRepository(db)
    service = WalletService(repository, verify_user_exists)
    data, code = await service.deposit(userId, payload.amount, payload.externalOperationId, payload.reason, trace_id)
    if code == Codes.INVALID_REQUEST:
        return error_response(status_code=400, message="Amount must be greater than 0", code=code, trace_id=trace_id)
    if code == Codes.USER_NOT_FOUND:
        return error_response(status_code=404, message=f"User with id {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_OPERATION_DUPLICATE:
        return error_response(status_code=409, message="Duplicate operation", code=code, trace_id=trace_id)
    return success_response(message="Deposit successful", code=code, data=data, trace_id=trace_id)


@router.post("/{userId}/withdraw")
async def withdraw_endpoint(request: Request, userId: str, payload: WithdrawRequest, db: AsyncSession = Depends(get_db)):
    """
    Снять средства с кошелька пользователя.
    Проверяет корректность суммы, наличие средств, дублирование операции и существование пользователя.
    """
    trace_id = getattr(request.state, 'trace_id', None)
    repository = WalletRepository(db)
    service = WalletService(repository, verify_user_exists)
    data, code = await service.withdraw(userId, payload.amount, payload.externalOperationId, payload.reason, trace_id)
    if code == Codes.INVALID_REQUEST:
        return error_response(status_code=400, message="Amount must be greater than 0", code=code, trace_id=trace_id)
    if code == Codes.USER_NOT_FOUND:
        return error_response(status_code=404, message=f"User with id {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_NOT_FOUND:
        return error_response(status_code=404, message=f"Wallet for user {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_OPERATION_DUPLICATE:
        return error_response(status_code=409, message="Duplicate operation", code=code, trace_id=trace_id)
    if code == Codes.WALLET_INSUFFICIENT_FUNDS:
        return error_response(status_code=400, message="Insufficient funds", code=code, trace_id=trace_id)
    return success_response(message="Withdrawal successful", code=code, data=data, trace_id=trace_id)


@router.delete("/{userId}")
async def delete_wallet_endpoint(request: Request, userId: str, db: AsyncSession = Depends(get_db)):
    """
    Удалить кошелёк пользователя. Возвращает ошибку, если кошелёк не найден или не пустой.
    """
    trace_id = getattr(request.state, 'trace_id', None)
    repository = WalletRepository(db)
    service = WalletService(repository, verify_user_exists)
    data, code = await service.delete_wallet(userId)
    if code == Codes.USER_NOT_FOUND:
        return error_response(status_code=404, message=f"User with id {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_NOT_FOUND:
        return error_response(status_code=404, message=f"Wallet for user {userId} not found", code=code, trace_id=trace_id)
    if code == Codes.WALLET_NOT_EMPTY:
        return error_response(status_code=409, message="Wallet is not empty", code=code, trace_id=trace_id)
    return success_response(message="Wallet deleted successfully", code=code, data=None, trace_id=trace_id)
