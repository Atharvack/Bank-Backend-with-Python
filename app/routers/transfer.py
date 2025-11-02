from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import uuid

from ..utils.database import get_db
from ..utils.models import Account, Transaction
from ..utils import schemas

router = APIRouter(prefix="/api/v2/transfers", tags=["transfers"])


@router.post(
    "/", response_model=schemas.TransferResponse, status_code=status.HTTP_201_CREATED,summary="Perform a Transfer between two Accounts. -- ASSESSMENT FUNCTIONALITY --"
)
def create_transfer(transfer: schemas.TransferCreate, db: Session = Depends(get_db)):
    """
    Transfer amounts between any two accounts, including those owned by different customers.

    This endpoint creates TWO transactions:
    1. A debit transaction on the source account (negative amount)
    2. A credit transaction on the destination account (positive amount)

    Both transactions are linked by a shared transferId for logging purposes.
    """

    if (
        transfer.fromAccountId == transfer.toAccountId
    ):  # Validate accounts are different
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer to the same account",
        )

    fromAccount = (
        db.query(Account).filter(Account.accountId == transfer.fromAccountId).first()
    )
    toAccount = (
        db.query(Account).filter(Account.accountId == transfer.toAccountId).first()
    )

    if not fromAccount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source account {transfer.fromAccountId} not found",
        )

    if not toAccount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination account {transfer.toAccountId} not found",
        )

    # Check sufficient funds
    if fromAccount.balance < transfer.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds in account {transfer.fromAccountId}. "
            f"Balance: {fromAccount.balance}, Required: {transfer.amount}",
        )

    # Generate unique transferId to link the two transactions
    transferIdValue = str(uuid.uuid4())

    try:
        # Create debit transaction (from account)
        debitTransaction = Transaction(
            accountId=transfer.fromAccountId,
            amount=-transfer.amount,  # Negative for debit
            name=transfer.description or f"Transfer to {toAccount.name}",
            transferId=transferIdValue,
            currency=fromAccount.currency,
        )
        db.add(debitTransaction)

        # Create credit transaction (to account)
        creditTransaction = Transaction(
            accountId=transfer.toAccountId,
            amount=transfer.amount,  # Positive for credit
            name=transfer.description or f"Transfer from {fromAccount.name}",
            transferId=transferIdValue,
            currency=toAccount.currency,
        )
        db.add(creditTransaction)

        # Update account balances
        fromAccount.balance -= transfer.amount
        toAccount.balance += transfer.amount

        db.commit()

        # Refresh to get generated IDs
        db.refresh(debitTransaction)
        db.refresh(creditTransaction)

        return schemas.TransferResponse(
            transferId=transferIdValue,
            fromTransactionId=debitTransaction.transactionId,
            toTransactionId=creditTransaction.transactionId,
            fromAccountId=transfer.fromAccountId,
            toAccountId=transfer.toAccountId,
            amount=transfer.amount,
            status="success",
            message=f"Successfully transferred {transfer.amount} from account {fromAccount.name} to {toAccount.name}",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer failed: {str(e)}",
        )


@router.get("/{transferId}", response_model=dict)
def get_transfer(transferId: str, db: Session = Depends(get_db)):
    """
    Find credit and debit transactions with this transferId
    """
    transactions = (
        db.query(Transaction).filter(Transaction.transferId == transferId).all()
    )

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transfer with ID {transferId} not found",
        )

    if len(transactions) != 2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid transfer state: expected 2 transactions, found {len(transactions)}",
        )

    # Identify debit and credit transactions
    debitTxn = next((t for t in transactions if t.amount < 0), None)
    creditTxn = next((t for t in transactions if t.amount > 0), None)

    return {
        "transferId": transferId,
        "debitTransaction": {
            "transactionId": debitTxn.transactionId,
            "accountId": debitTxn.accountId,
            "amount": debitTxn.amount,
            "date": debitTxn.date,
        },
        "creditTransaction": {
            "transactionId": creditTxn.transactionId,
            "accountId": creditTxn.accountId,
            "amount": creditTxn.amount,
            "date": creditTxn.date,
        },
        "totalAmount": abs(debitTxn.amount),
        "status": "completed",
    }
