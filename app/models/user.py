from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import Boolean


class UserORM(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


    courses: Mapped[List['CourseORM']] = relationship('CourseORM', back_populates='teacher')
    subscriptions: Mapped[List['SubscriptionORM']] = relationship('SubscriptionORM', back_populates='student')


