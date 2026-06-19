from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import TransactionStatus


class SimulateRequest(BaseModel):
    count: int = Field(default=25, ge=1, le=500)
    failure_rate: float | None = Field(default=None, ge=0, le=1)


class TransactionOut(BaseModel):
    id: str
    reference: str
    account_id: str
    channel: str
    amount: Decimal
    currency: str
    status: TransactionStatus
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HistoryOut(BaseModel):
    status: TransactionStatus
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionDetail(TransactionOut):
    history: list[HistoryOut]


class AlertOut(BaseModel):
    id: int
    severity: str
    title: str
    message: str
    threshold: int
    observed_value: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    actor: str
    event_type: str
    message: str
    correlation_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

