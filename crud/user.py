import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from schemas.user import UserRegister, UserLogin


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, payload: UserLogin) -> User | None:
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, payload: UserRegister) -> User:
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
