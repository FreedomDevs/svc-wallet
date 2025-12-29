from app.repository.wallet_repository import WalletRepository
from app.db.models import WalletOperation, WalletOperationType
from app.codes import Codes
from uuid import uuid4
from app.core.utils import get_timestamp

class WalletService:
    """
    Сервис для бизнес-логики работы с кошельками: создание, получение, пополнение, списание, удаление.
    Использует репозиторий и функцию проверки пользователя.
    """
    def __init__(self, repository: WalletRepository, verify_user_exists):
        """
        :param repository: Репозиторий для работы с БД
        :param verify_user_exists: функция проверки существования пользователя
        """
        self.repository = repository
        self.verify_user_exists = verify_user_exists

    async def create_wallet(self, user_id: str):
        """
        Создать кошелёк для пользователя, если он существует и кошелёк ещё не создан.
        :return: данные кошелька и код результата
        """
        if not await self.verify_user_exists(user_id):
            return None, Codes.USER_NOT_FOUND
        existing = await self.repository.get_wallet_by_user_id(user_id)
        if existing:
            return None, Codes.WALLET_ALREADY_EXISTS
        wallet = await self.repository.create_wallet(user_id)
        balance = await self.repository.get_balance(wallet.id)
        return {"id": wallet.id, "userId": wallet.userId, "balance": balance}, Codes.WALLET_CREATED

    async def get_wallet(self, user_id: str):
        """
        Получить кошелёк пользователя, если он и кошелёк существуют.
        :return: данные кошелька и код результата
        """
        if not await self.verify_user_exists(user_id):
            return None, Codes.USER_NOT_FOUND
        wallet = await self.repository.get_wallet_by_user_id(user_id)
        if not wallet:
            return None, Codes.WALLET_NOT_FOUND
        balance = await self.repository.get_balance(wallet.id)
        return {"id": wallet.id, "userId": wallet.userId, "balance": balance}, Codes.WALLET_FETCHED_OK

    async def deposit(self, user_id: str, amount: int, external_id: str, reason: str, trace_id: str):
        """
        Пополнить баланс кошелька пользователя. Создаёт кошелёк при необходимости.
        Проверяет дублирование операции и корректность суммы.
        :return: новые данные кошелька и код результата
        """
        if amount <= 0:
            return None, Codes.INVALID_REQUEST
        if not await self.verify_user_exists(user_id):
            return None, Codes.USER_NOT_FOUND
        wallet = await self.repository.get_wallet_by_user_id(user_id)
        if not wallet:
            wallet = await self.repository.create_wallet(user_id)
        if await self.repository.get_operation_by_external_id(external_id):
            return None, Codes.WALLET_OPERATION_DUPLICATE
        operation = WalletOperation(
            id=str(uuid4()),
            walletId=wallet.id,
            amount=amount,
            type=WalletOperationType.DEPOSIT.value,
            reason=reason,
            externalOperationId=external_id,
            traceId=trace_id or "",
            createdAt=get_timestamp()
        )
        await self.repository.add_operation(operation)
        balance = await self.repository.get_balance(wallet.id)
        return {"id": wallet.id, "userId": wallet.userId, "balance": balance}, Codes.WALLET_DEPOSIT_OK

    async def withdraw(self, user_id: str, amount: int, external_id: str, reason: str, trace_id: str):
        """
        Списать средства с кошелька пользователя. Проверяет баланс, дублирование операции и корректность суммы.
        :return: новые данные кошелька и код результата
        """
        if amount <= 0:
            return None, Codes.INVALID_REQUEST
        if not await self.verify_user_exists(user_id):
            return None, Codes.USER_NOT_FOUND
        wallet = await self.repository.get_wallet_by_user_id(user_id)
        if not wallet:
            return None, Codes.WALLET_NOT_FOUND
        if await self.repository.get_operation_by_external_id(external_id):
            return None, Codes.WALLET_OPERATION_DUPLICATE
        balance = await self.repository.get_balance(wallet.id)
        if balance < amount:
            return None, Codes.WALLET_INSUFFICIENT_FUNDS
        operation = WalletOperation(
            id=str(uuid4()),
            walletId=wallet.id,
            amount=-amount,
            type=WalletOperationType.WITHDRAW.value,
            reason=reason,
            externalOperationId=external_id,
            traceId=trace_id or "",
            createdAt=get_timestamp()
        )
        await self.repository.add_operation(operation)
        balance = await self.repository.get_balance(wallet.id)
        return {"id": wallet.id, "userId": wallet.userId, "balance": balance}, Codes.WALLET_WITHDRAW_OK

    async def delete_wallet(self, user_id: str):
        """
        Удалить кошелёк пользователя, если он существует и баланс равен 0.
        :return: None и код результата
        """
        if not await self.verify_user_exists(user_id):
            return None, Codes.USER_NOT_FOUND
        wallet = await self.repository.get_wallet_by_user_id(user_id)
        if not wallet:
            return None, Codes.WALLET_NOT_FOUND
        balance = await self.repository.get_balance(wallet.id)
        if balance != 0:
            return None, Codes.WALLET_NOT_EMPTY
        await self.repository.delete_wallet(wallet)
        return None, Codes.WALLET_DELETED
