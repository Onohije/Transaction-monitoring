import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .models import Alert, AuditLog, Transaction, TransactionHistory, TransactionStatus

FAILURE_REASONS = [
    "VALIDATION_FAILED",
    "INSUFFICIENT_FUNDS",
    "HOST_TIMEOUT",
    "REVERSAL_REQUIRED",
    "DUPLICATE_REFERENCE",
]
CHANNELS = ["ATM", "MOBILE", "INTERNET_BANKING", "POS", "BRANCH"]


def log_event(db: Session, event_type: str, message: str, correlation_id: str | None = None, actor: str = "system") -> None:
    db.add(AuditLog(actor=actor, event_type=event_type, message=message, correlation_id=correlation_id))


def add_history(db: Session, tx: Transaction, status: TransactionStatus, reason: str | None = None) -> None:
    tx.status = status
    tx.failure_reason = reason if status == TransactionStatus.FAILED else None
    db.add(TransactionHistory(transaction=tx, status=status, reason=reason))
    log_event(db, "TRANSACTION_STATUS_CHANGED", f"{tx.reference} moved to {status}", tx.reference)


def simulate_transactions(db: Session, count: int, failure_rate: float | None = None) -> list[Transaction]:
    actual_failure_rate = settings.sim_failure_rate if failure_rate is None else failure_rate
    created: list[Transaction] = []

    for _ in range(count):
        tx = Transaction(
            reference=f"TX-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:10].upper()}",
            account_id=f"ACCT-{random.randint(100000, 999999)}",
            channel=random.choice(CHANNELS),
            amount=Decimal(random.randint(100, 2_500_000)) / Decimal("100"),
            currency="USD",
            status=TransactionStatus.RECEIVED,
        )
        db.add(tx)
        db.flush()
        add_history(db, tx, TransactionStatus.RECEIVED)
        add_history(db, tx, TransactionStatus.VALIDATED)

        if random.random() < actual_failure_rate:
            add_history(db, tx, TransactionStatus.FAILED, random.choice(FAILURE_REASONS))
        else:
            add_history(db, tx, TransactionStatus.POSTED)
            add_history(db, tx, TransactionStatus.SETTLED)
        created.append(tx)

    log_event(db, "SIMULATION_RUN", f"Generated {count} transactions with failure rate {actual_failure_rate:.2%}")
    maybe_raise_failed_transaction_alert(db)
    db.commit()
    return created


def maybe_raise_failed_transaction_alert(db: Session) -> None:
    window_start = datetime.now(timezone.utc) - timedelta(seconds=settings.failed_tx_window_seconds)
    failed_count = db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= window_start,
        )
    )
    if failed_count and failed_count >= settings.failed_tx_threshold:
        alert = Alert(
            severity="HIGH",
            title="Failed transaction threshold breached",
            message=f"{failed_count} failed transactions observed in the last {settings.failed_tx_window_seconds} seconds.",
            threshold=settings.failed_tx_threshold,
            observed_value=failed_count,
        )
        db.add(alert)
        log_event(db, "ALERT_CREATED", alert.message)


def get_transaction_detail(db: Session, tx_id: str) -> Transaction | None:
    return db.scalar(
        select(Transaction)
        .where(Transaction.id == tx_id)
        .options(selectinload(Transaction.history))
    )

