"""
- UUID strings work as primary keys (not integers) for better security and scalability
- Numeric type for all money fields to avoid floating-point precision errors
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from .database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Customer(Base):
    """
    Customer model
    A customer can own multiple accounts and perform transactions.

    Attributes:
        customerId: Primary key - Unique UUID identifier for the customer
        email: Unique email address
        firstName:
        lastName:
        phoneNumber: Optional
        createdAt: Timestamp when the customer was created
        updatedAt: Timestamp when the customer was last updated
        accounts: Relationship to Account model (one-to-many)
    """

    __tablename__ = "customers"

    customerId = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True)
    createdAt = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updatedAt = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # One customer can own many accounts, Relationship: One to Many
    accounts = relationship(
        "Account", back_populates="owner", cascade="all, delete-orphan"
    )


class Account(Base):
    """
    Account model

    Attributes:
        accountId: Primary key - Unique UUID identifier
        customerId: Foreign key to customers table
        name: Account name/nickname

        accountType: Type of account from (checking, savings)
        balance:
        currency: Currency code ("USD", "EUR")
        createdAt: Timestamp when the account was created
        updatedAt: Timestamp when the account was last updated
        owner: Relationship to Customer model
        transactions: Relationship to Transaction model
    """

    __tablename__ = "accounts"

    accountId = Column(String, primary_key=True, default=generate_uuid, index=True)
    customerId = Column(
        String,
        ForeignKey("customers.customerId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)

    accountType = Column(String, nullable=False)  # checking or savings for now
    balance = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False, default="USD")
    createdAt = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updatedAt = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("Customer", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """
    Transaction model - single ledger entry (a debit or a credit).

    A transfer between two accounts is represented by two separate Transaction records
    (one debit, one credit) that are linked by a common `transferId`.

    Attributes:
        transactionId: Primary key - Unique UUID identifier for the transaction
        accountId: Foreign key to the account this transaction belongs to
        amount: Transaction amount (Numeric for precision, negative for debits)
        date: Transaction date and time
        name: Transaction description/name

        transferId: A shared UUID used to link the debit and credit transactions of a single transfer

        currency: Currency code ("USD", "EUR")
        createdAt: Timestamp when the transaction was created
        account:
    """

    __tablename__ = "transactions"

    transactionId = Column(String, primary_key=True, default=generate_uuid, index=True)
    accountId = Column(
        String,
        ForeignKey("accounts.accountId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(10, 2), nullable=False)

    date = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    name = Column(String, nullable=False)

    transferId = Column(
        String, nullable=True, index=True
    )  # will be null for non-transfer transactions like deposits or purchases if support added.
    currency = Column(String, nullable=False, default="USD")
    createdAt = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    account = relationship("Account", back_populates="transactions")
