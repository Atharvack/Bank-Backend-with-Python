from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utils.database import init_db
from .routers import customer, account, transfer, transaction


APP_Version = "1.0.4"
# Initialize FastAPI application
app = FastAPI(
    title="Meow Financial Institution API",
    version=APP_Version,
    description="""


Fake Financial Institution API

### Testing Workflow

Advised Steps for testing:

1.  **Create a Customer:** [Creation of customers is prerequisite for creating Financial Institute accounts.]
    *   Go to the `POST /api/v1/customers` endpoint.
    *   Create one or two customers.
    *   Copy the `customerId` from the response for the next step.

2.  **Create Financial Institute Account(s):**
    *   Go to the `POST /api/v1/accounts` endpoint.
    *   Use a `customerId` from the previous step to create one or more Financial Institute accounts.
    *   Copy the `accountId` from the response for the next step.

3.  **Perform a Transfer:**
    *   Go to the `POST /api/v2/transfers` endpoint.
    *   Use the `accountId` values from the accounts you created to transfer funds between them.


### Transfers vs. Transactions

In this API, these two concepts are related but distinct:

*   **Transfer**: A 'Transfer' is the *action* you initiate via the `POST /api/v2/transfers` endpoint. It represents the complete operation of moving funds from one account to another.

*   **Transaction**: A 'Transaction' is a single *record* in the Financial Institution's ledger. A single Transfer action automatically creates **two** `Transaction` records:
    *   A **debit** transaction (negative amount) on the source account.
    *   A **credit** transaction (positive amount) on the destination account.

These two `Transaction` records are linked by a shared `transferId`.

""",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = ["http://localhost", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # rest are outside the scope for this assessment
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()
    print("✓ Database initialized")


app.include_router(customer.router)
app.include_router(account.router)
app.include_router(transfer.router)
app.include_router(transaction.router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Meow Financial Institution API",
        "version": APP_Version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "customers": "/api/v1/customers",
            "accounts": "/api/v1/accounts",
            "transfers": "/api/v2/transfers",
            "transactions": "/api/v2/transactions",
        },
    }
