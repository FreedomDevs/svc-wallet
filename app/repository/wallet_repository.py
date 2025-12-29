from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.db.models import Wallet, WalletOperation
from uuid import uuid4
from typing import Optional

class WalletRepository:
    """
    Репозиторий для работы с кошельками и операциями в базе данных.
    """
    def __init__(self, db: AsyncSession):
        """
        :param db: асинхронная сессия SQLAlchemy
        """
        self.db = db

    async def get_wallet_by_user_id(self, user_id: str) -> Optional[Wallet]:
        """
        Получить кошелёк по user_id.
        :return: Wallet или None
        """
        result = await self.db.execute(select(Wallet).where(Wallet.userId == user_id))
        return result.scalar_one_or_none()

    async def create_wallet(self, user_id: str) -> Wallet:
        """
        Создать новый кошелёк для пользователя.
        :return: созданный Wallet
        """
        wallet_id = str(uuid4())
        wallet = Wallet(id=wallet_id, userId=user_id)
        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    async def delete_wallet(self, wallet: Wallet):
        """
        Удалить кошелёк из базы данных.
        """
        await self.db.delete(wallet)
        await self.db.commit()

    async def get_balance(self, wallet_id: str) -> int:
        """
        Получить текущий баланс кошелька по wallet_id.
        :return: сумма баланса (int)
        """
        from sqlalchemy import func
        op_result = await self.db.execute(
            select(func.coalesce(func.sum(WalletOperation.amount), 0)).where(WalletOperation.walletId == wallet_id)
        )
        return op_result.scalar_one()

    async def add_operation(self, operation: WalletOperation):
        """
        Добавить операцию (пополнение/списание) в базу данных.
        """
        self.db.add(operation)
        await self.db.commit()

    async def get_operation_by_external_id(self, external_id: str) -> Optional[WalletOperation]:
        """
        Получить операцию по внешнему идентификатору (для защиты от дублей).
        :return: WalletOperation или None
        """
        result = await self.db.execute(select(WalletOperation).where(WalletOperation.externalOperationId == external_id))
        return result.scalar_one_or_none()
