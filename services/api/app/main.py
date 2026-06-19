from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Alert, AuditLog, Transaction, TransactionStatus
from .schemas import AlertOut, AuditLogOut, SimulateRequest, TransactionDetail, TransactionOut
from .services import get_transaction_detail, simulate_transactions

app = FastAPI(title="Bank Transaction Monitoring API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

TX_CREATED = Counter("bankmon_transactions_created_total", "Transactions created", ["status"])
FAILED_GAUGE = Gauge("bankmon_failed_transactions", "Current failed transaction count")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok"}


@app.post("/simulate", response_model=list[TransactionOut])
def simulate(payload: SimulateRequest, db: Session = Depends(get_db)):
    rows = simulate_transactions(db, payload.count, payload.failure_rate)
    for row in rows:
        TX_CREATED.labels(status=row.status.value).inc()
    return rows


@app.get("/transactions", response_model=list[TransactionOut])
def transactions(
    status: TransactionStatus | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Transaction).order_by(desc(Transaction.created_at)).limit(limit)
    if status:
        stmt = stmt.where(Transaction.status == status)
    return db.scalars(stmt).all()


@app.get("/transactions/{tx_id}", response_model=TransactionDetail)
def transaction_detail(tx_id: str, db: Session = Depends(get_db)):
    tx = get_transaction_detail(db, tx_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@app.get("/alerts", response_model=list[AlertOut])
def alerts(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(Alert).order_by(desc(Alert.created_at)).limit(limit)).all()


@app.get("/logs", response_model=list[AuditLogOut])
def logs(limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)).all()


@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    rows = db.execute(select(Transaction.status, func.count(Transaction.id)).group_by(Transaction.status)).all()
    data = {status.value: count for status, count in rows}
    FAILED_GAUGE.set(data.get("FAILED", 0))
    return {
        "total": sum(data.values()),
        "by_status": data,
        "failed": data.get("FAILED", 0),
        "settled": data.get("SETTLED", 0),
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
