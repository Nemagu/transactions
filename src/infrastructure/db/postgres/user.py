from uuid import UUID

from psycopg.sql import SQL, Identifier

from application.ports.repositories import UserReadRepository
from domain.user import User, UserFactory, UserID
from infrastructure.db.postgres.base import BasePostgresRepository, handle_domain_errors


class UserReadPostgresRepository(BasePostgresRepository, UserReadRepository):
    async def by_id(self, user_id: UserID) -> User | None:
        query = SQL(
            """
            SELECT
                user_id,
                state,
                version
            FROM {}
            WHERE user_id = %s
            """
        ).format(Identifier(self._user_tables.read))
        data = await self._fetchone(query, (user_id.user_id,))
        return self._data_to_domain(data) if data is not None else None

    async def save(self, user: User) -> None:
        if user.version.version == 1:
            await self._create(user)
        else:
            await self._update(user)

    async def _create(self, user: User) -> None:
        query = SQL(
            """
            INSERT INTO {} (
                user_id,
                state,
                version
            )
            VALUES (%s, %s, %s)
            """
        ).format(Identifier(self._user_tables.read))
        await self._execute(
            query, (user.user_id.user_id, user.state.value, user.version.version)
        )

    async def _update(self, user: User) -> None:
        query = SQL(
            """
            UPDATE {}
            SET state = %s, version = %s
            WHERE user_id = %s
            """
        ).format(Identifier(self._user_tables.read))
        await self._execute(
            query, (user.state.value, user.version.version, user.user_id.user_id)
        )

    @handle_domain_errors
    def _data_to_domain(self, data: tuple[UUID, str, int]) -> User:
        return UserFactory.restore(*data)
