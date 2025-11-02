from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..utils.database import get_db
from ..utils.models import Account, Transaction
from ..utils import schemas

router = APIRouter(prefix="/api/v2/transactions", tags=["transactions"])


@router.get("/account/{accountId}", response_model=List[schemas.Transaction],summary="Get all Transactions linked to an AccountID. -- ASSESSMENT FUNCTIONALITY --")
def get_account_transactions(
    accountId: str,
    skip: int = 0,
    limit: int = 100,
    startDate: Optional[datetime] = None,
    endDate: Optional[datetime] = None,
    transfersOnly: bool = False,  # non-transfer transactions can be added and excluded here if True
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.accountId == accountId).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {accountId} not found",
        )

    query = db.query(Transaction).filter(Transaction.accountId == accountId)

    """
       Transfer only filter can be added here, currently outside the scope of assessment

    """

    if startDate:
        query = query.filter(Transaction.date >= startDate)

    if endDate:
        query = query.filter(Transaction.date <= endDate)

    transactions = (
        query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    )

    return transactions


@router.get("/{transactionId}", response_model=schemas.Transaction,summary="Get account linked Transaction by TransactionID")
def get_transaction(transactionId: str, db: Session = Depends(get_db)):
    """
    Get transaction details by transactionId
    Helper Service to fetch transaction details
    """
    transaction = (
        db.query(Transaction).filter(Transaction.transactionId == transactionId).first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transactionId} not found",
        )

    return transaction



