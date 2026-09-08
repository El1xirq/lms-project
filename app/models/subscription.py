from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func, Boolean, DateTime, Index, text
from datetime import datetime, timedelta, timezone



class SubscriptionORM(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (
        Index(
            "uq_active_subscription_student_course",
            "student_id",
            "course_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='RESTRICT'), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(days=30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


    student: Mapped['UserORM'] = relationship('UserORM', back_populates='subscriptions')
    course: Mapped['CourseORM'] = relationship('CourseORM', back_populates='subscriptions')


    @property
    def course_title(self) -> str:
        return self.course.title if self.course else ""