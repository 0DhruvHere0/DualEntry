# DualEntry

DualEntry is a backend REST API for double-entry bookkeeping and financial reporting.

The project models core accounting concepts such as users, accounts, counterparties, transactions, and journal entries. It validates transactions according to double-entry accounting rules and generates financial reports including trial balances, account ledgers, income statements, and balance sheets.

The application also provides Excel export functionality for financial reports.

## Features

- User management
- Multiple accounts per user
- Account categories:
  - Asset
  - Liability
  - Equity
  - Income
  - Expense
- Counterpart management with relationship types
- Double-entry transactions
- Debit and credit validation
- Transaction-specific account validation
- Account balance calculation
- Account ledger generation with running balances
- Trial balance generation
- Income statement generation
- Balance sheet generation
- Excel financial report export
- PostgreSQL database
- Alembic database migrations
- Automatic request and response validation using Pydantic

## Tech Stack

- **Python**
- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM and database interaction
- **PostgreSQL** — relational database
- **Pydantic** — request/response validation
- **Alembic** — database migrations
- **Uvicorn** — ASGI server
- **openpyxl** — Excel report generation

## Architecture

The application follows a layered structure separating API routes, database models, schemas, and reusable services.

```text
app/
├── api/
│   ├── router.py
│   └── routes/
│       ├── account.py
│       ├── counterpart.py
│       ├── health.py
│       ├── report.py
│       ├── transaction.py
│       └── user.py
│
├── database/
│   ├── base.py
│   ├── dependency.py
│   └── session.py
│
├── models/
│   ├── account.py
│   ├── counterpart.py
│   ├── entry.py
│   ├── transaction.py
│   └── user.py
│
├── schemas/
│   ├── account.py
│   ├── counterpart.py
│   ├── report.py
│   ├── transaction.py
│   └── user.py
│
├── services/
│   └── excel_export.py
│
└── main.py
```

### Directory responsibilities

| Directory | Responsibility |
|---|---|
| `api/routes` | HTTP endpoints and API logic |
| `database` | Database engine, sessions, and dependencies |
| `models` | SQLAlchemy database models |
| `schemas` | Pydantic request/response schemas |
| `services` | Reusable application services |
| `alembic` | Database migration history |

## Accounting Model

DualEntry uses the fundamental double-entry accounting principle:

```text
Total Debits = Total Credits
```

Every transaction contains one or more debit and credit entries.

For example, purchasing office supplies for 1,000 using cash:

```text
Debit   Office Expense    1,000
Credit  Cash              1,000
```

The transaction is accepted only when:

```text
Total Debits = Total Credits
```

Amounts must also be greater than zero.

## Transaction Types

The API currently supports the following transaction types:

```text
SALE
PURCHASE
EXPENSE
INCOME
LOAN_RECEIVED
LOAN_GIVEN
LOAN_REPAYMENT
RECEIPT
PAYMENT
TRANSFER
```

Transaction entries use one of two entry types:

```text
DEBIT
CREDIT
```

The transaction API currently applies explicit account-category validation for:

- `SALE`
- `PURCHASE`
- `EXPENSE`
- `INCOME`

For example, a `SALE` requires:

```text
Debit  → Asset account
Credit → Income account
```

A `PURCHASE` allows:

```text
Debit  → Asset or Expense account
Credit → Asset or Liability account
```

## Data Model

The main entities are:

```text
User
 │
 ├── Accounts
 │      │
 │      └── Entries
 │
 ├── Counterpart Relationships
 │
 └── Transactions
        │
        └── Entries
```

### User

Represents the owner of the accounting data.

### Account

Represents a financial account belonging to a user.

Accounts have a category such as:

```text
Asset
Liability
Equity
Income
Expense
```

Multiple accounts with the same name are allowed for the same user.

### Counterpart

Represents another user involved in a business relationship.

Examples of relationship types include:

```text
CUSTOMER
SUPPLIER
LENDER
BORROWER
```

A transaction requires an existing counterpart relationship between the two users.

### Transaction

Represents a business event such as a sale or purchase.

A transaction contains:

- User
- Counterpart
- Transaction type
- Description
- Journal entries
- Creation timestamp

### Entry

Represents an individual debit or credit posted to an account.

Each entry contains:

- Account
- Entry type
- Amount
- Transaction

## API Endpoints

### Health

```http
GET /health
```

Returns the application health/status.

### Users

```http
POST /users/
GET /users/{user_id}
```

Creates and retrieves users.

### Accounts

```http
POST /accounts/
GET /accounts/{account_id}/balance
GET /accounts/{account_id}/entries
```

Creates accounts and retrieves account balances and journal entries.

### Counterparts

```http
POST /counterparts/
GET /counterparts/user/{user_id}
```

Creates and retrieves counterpart relationships.

The counterpart listing also supports filtering by relationship type.

### Transactions

```http
POST /transactions/
GET /transactions/user/{user_id}
GET /transactions/{transaction_id}
```

Creates and retrieves transactions.

### Reports

```http
GET /reports/trial-balance/{user_id}
GET /reports/account-ledger/{account_id}
GET /reports/income-statement/{user_id}
GET /reports/balance-sheet/{user_id}
GET /reports/export/{user_id}
```

The export endpoint generates an Excel workbook containing financial reports.

## Transaction Validation

Before a transaction is stored, the API performs several validations.

### User validation

The transaction user must exist.

### Counterpart validation

The counterpart user must exist and cannot be the same as the transaction user.

An established counterpart relationship is also required.

### Account validation

Every referenced account must:

1. Exist
2. Belong to the transaction user

This prevents users from posting entries to another user's accounts.

### Debit/Credit validation

Every transaction must contain both debit and credit entries.

```text
Debit total = Credit total
```

Otherwise the transaction is rejected.

### Positive amounts

Entry amounts must be greater than zero.

For example:

```json
{
  "amount": -1000
}
```

is rejected during request validation.

## Financial Reports

### Trial Balance

The trial balance summarizes debit and credit totals for every account.

The report verifies that:

```text
Total Debit = Total Credit
```

### Account Ledger

The account ledger displays individual entries for an account along with a running balance.

For an Asset account:

```text
Debit  → increases balance
Credit → decreases balance
```

For Liability, Equity, and Income accounts, the normal balance direction is reversed.

### Income Statement

The income statement calculates:

```text
Net Income = Total Income - Total Expenses
```

For example:

```text
Income       2,000
Expenses     1,000
-------------------
Net Income   1,000
```

### Balance Sheet

The balance sheet organizes accounts into:

```text
Assets
Liabilities
Equity
```

and verifies the accounting equation:

```text
Assets = Liabilities + Equity
```

Current profit is included as part of equity.

## Excel Export

The financial report export endpoint generates an `.xlsx` workbook containing:

```text
Trial Balance
Account Ledgers
Income Statement
Balance Sheet
```

The workbook is generated in memory using `openpyxl` and returned as a downloadable response.

## Database Migrations

DualEntry uses Alembic to manage database schema changes.

To apply migrations:

```bash
alembic upgrade head
```

To create a new migration:

```bash
alembic revision --autogenerate -m "describe change"
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd DualEntry
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and configure the application's database connection according to the project's environment configuration.

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Example Transaction

A simple cash sale of 2,000 can be represented as:

```json
{
  "user_id": 3,
  "counterpart_id": 4,
  "transaction_type": "SALE",
  "description": "Cash sale",
  "entries": [
    {
      "account_id": 15,
      "entry_type": "DEBIT",
      "amount": 2000
    },
    {
      "account_id": 18,
      "entry_type": "CREDIT",
      "amount": 2000
    }
  ]
}
```

The accounting effect is:

```text
Cash                 +2,000
Sales Income         +2,000
```

The transaction satisfies:

```text
Debit  = 2,000
Credit = 2,000
```

## Example Financial Flow

A purchase followed by a sale demonstrates how transactions flow through the accounting system.

```text
Purchase
   │
   ├── Debit Expense
   └── Credit Cash
          │
          ▼
       Account Ledger
          │
          ▼
    Financial Reports
          │
          ├── Trial Balance
          ├── Income Statement
          └── Balance Sheet
```

## Project Status

DualEntry currently provides the core backend functionality for:

- Double-entry transaction recording
- Account balance tracking
- Counterpart relationships
- Financial statement generation
- Excel financial reporting
- Database migrations

## Future Improvements

Potential future improvements include:

- Automated test suite
- Authentication and authorization
- User-specific access control
- Expanded validation for all transaction types
- Date-range filtering for reports
- Pagination for transaction and ledger endpoints
- CSV/PDF report exports
- Improved financial report formatting
- API versioning
- Docker-based deployment
- CI/CD pipeline