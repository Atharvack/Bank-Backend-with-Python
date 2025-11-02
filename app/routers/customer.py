from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..utils.database import get_db
from ..utils.models import Customer
from ..utils import schemas

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.post("/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer
    Helper Service to create customers for creating Financial Institute accounts
    """
    existingCustomer = (
        db.query(Customer).filter(Customer.email == customer.email).first()
    )  # Check if email already exists

    if existingCustomer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with email {customer.email} already exists",
        )

    dbCustomer = Customer(**customer.model_dump())
    db.add(dbCustomer)
    db.commit()
    db.refresh(dbCustomer)

    return dbCustomer


@router.get("/{customerId}", response_model=schemas.CustomerWithAccounts,summary="Get Customer Details and exisitng Accounts")
def get_customer(customerId: str, db: Session = Depends(get_db)):
    """
    List customer details and accounts by customerId
    Helper Service to fetch customer details
    """
    
    customer = db.query(Customer).filter(Customer.customerId == customerId).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customerId} not found",
        )

    return customer


@router.get("/", response_model=List[schemas.Customer])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all customers
    Helper Service to fetch all customers"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers
