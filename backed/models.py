from datetime import time, date, datetime
from sqlalchemy import Integer, String, Time, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    duty_location: Mapped[str] = mapped_column(String)
    duty_start_time: Mapped[str] = mapped_column(String)
    duty_end_time: Mapped[str] = mapped_column(String)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    openid: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    student_id: Mapped[str] = mapped_column(String, unique=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))


class AdminScope(Base):
    __tablename__ = "admin_scope"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))


class DutyRecord(Base):
    __tablename__ = "duty_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))
    record_date: Mapped[date] = mapped_column(Date)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=True)
    photo_url: Mapped[str] = mapped_column(String, nullable=True)
    upload_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_unqualified: Mapped[bool] = mapped_column(Boolean, default=False)
    unqualified_reason: Mapped[str] = mapped_column(String, nullable=True)
    unqualified_photos: Mapped[str] = mapped_column(String, nullable=True)  # 存JSON字符串
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=True)
    last_edit_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_base64: Mapped[str] = mapped_column(String, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=False)
    record_id: Mapped[int] = mapped_column(Integer, ForeignKey("duty_records.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
