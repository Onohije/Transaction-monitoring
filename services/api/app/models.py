import enum
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class TransactionStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    POSTED = "POSTED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    reference: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    account_id: Mapped[str] = mapped_column(String(32), index=True)
    channel: Mapped[str] = mapped_column(String(24), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), index=True)
    failure_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    history: Mapped[list["TransactionHistory"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")


class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("transactions.id"), index=True)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus))
    reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    transaction: Mapped[Transaction] = relationship(back_populates="history")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    title: Mapped[str] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(Text)
    threshold: Mapped[int] = mapped_column()
    observed_value: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor: Mapped[str] = mapped_column(String(64), default="system")
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


Index("idx_transactions_status_created", Transaction.status, Transaction.created_at)

