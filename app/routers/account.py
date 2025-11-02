from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from ..utils.database import get_db
from ..utils.models import Customer, Account
from ..utils import schemas

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.post("/", response_model=schemas.Account, status_code=status.HTTP_201_CREATED,summary="Create a new Financial Institute Account for existing Customer. -- ASSESSMENT FUNCTIONALITY --")
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new Financial Institute account for a customer
    Types of accounts could be 'savings', 'checking' for now.
    """
    customer = (
        db.query(Customer).filter(Customer.customerId == account.customerId).first()
    )  # Verify customer exists

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {account.customerId} not found",
        )

    dbAccount = Account(**account.model_dump())
    db.add(dbAccount)
    db.commit()
    db.refresh(dbAccount)

    return dbAccount


@router.get("/{accountId}/balance", response_model=schemas.AccountBalance,summary="Get current balance of an existing Account.-- ASSESSMENT FUNCTIONALITY --")
def get_account_balance(accountId: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.accountId == accountId).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {accountId} not found",
        )

    return schemas.AccountBalance(
        accountId=account.accountId,
        accountName=account.name,
        balance=account.balance,
        currency=account.currency,
        lastUpdated=account.updatedAt,
    )



@router.get("/", response_model=List[schemas.Account],summary="List all existing accounts")
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all Financial institute accounts
    Helper Service to fetch all accounts
    """
    query = db.query(Account)

    accounts = query.offset(skip).limit(limit).all()
    return accounts
