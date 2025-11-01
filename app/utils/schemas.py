from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional
from decimal import Decimal


#  Customer Schemas


class CustomerBase(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phoneNumber: Optional[str] = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    customerId: str = Field(...)
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerWithAccounts(Customer):
    accounts: List["Account"] = []  # default empty list

    model_config = ConfigDict(from_attributes=True)


# Accounts


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    accountType: str = Field(...)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("accountType")
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        allowed_types = ["checking", "savings"]  # Different Types of accounts
        if v.lower() not in allowed_types:
            raise ValueError(f'Account type must be one of: {", ".join(allowed_types)}')
        return v.lower()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if not v.isupper() or len(v) != 3:
            raise ValueError("Currency must be a 3-letter uppercase code (USD, EUR)")
        return v


class AccountCreate(AccountBase):
    customerId: str = Field(...)
    balance: Decimal = Field(..., gt=0)


class Account(AccountBase):
    accountId: str = Field(...)
    customerId: str = Field(...)
    balance: Decimal = Field(...)
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountWithTransactions(Account):
    transactions: List["Transaction"] = []  # default empty list

    model_config = ConfigDict(from_attributes=True)


# Transaction


class TransactionBase(BaseModel):
    amount: Decimal = Field(...)
    name: str = Field(..., min_length=1, max_length=200)

    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if not v.isupper() or len(v) != 3:
            raise ValueError("Currency must be a 3-letter uppercase code (USD, EUR)")
        return v


class TransactionCreate(TransactionBase):
    accountId: str = Field(...)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Transaction(TransactionBase):
    transactionId: str = Field(...)
    accountId: str = Field(...)
    date: datetime
    createdAt: datetime
    transferId: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)


# Transfer


class TransferCreate(BaseModel):
    """transfer between accounts, application logic will use this information to create two corresponding
    Transaction records in the database (one debit and one credit).
    """

    fromAccountId: str = Field(...)
    toAccountId: str = Field(...)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=200)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return v


class TransferResponse(BaseModel):
    transferId: str = Field(...)
    fromTransactionId: str = Field(...)
    toTransactionId: str = Field(...)
    fromAccountId: str
    toAccountId: str
    amount: Decimal
    status: str = Field(...)
    message: str = Field(...)


# Summary


class AccountSummary(BaseModel):
    accountId: str
    accountName: str
    balance: Decimal
    totalTransactions: int
    totalCredits: Decimal
    totalDebits: Decimal


class CustomerSummary(BaseModel):
    customerId: str
    fullName: str
    totalAccounts: int
    totalBalance: Decimal
    recentTransactions: int


#  Balance


class AccountBalance(BaseModel):
    accountId: str
    accountName: str
    balance: Decimal
    currency: str
    lastUpdated: datetime


# Enable forward references for nested models
CustomerWithAccounts.model_rebuild()
AccountWithTransactions.model_rebuild()
