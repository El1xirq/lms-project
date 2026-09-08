from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, DECIMAL
from datetime import datetime
from typing import List
from decimal import Decimal


class CourseORM(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


    teacher: Mapped['UserORM'] = relationship('UserORM', back_populates='courses')
    subscriptions: Mapped[List['SubscriptionORM']] = relationship('SubscriptionORM', back_populates='course')
