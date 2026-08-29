# DualEntry

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Alembic-1.13+-4C6EF5?style=for-the-badge&logo=alembic&logoColor=white" alt="Alembic">
  <img src="https://img.shields.io/badge/Pydantic-2.5+-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <strong>A robust backend REST API for double-entry bookkeeping and financial reporting</strong>
</p>

---

## Overview

DualEntry is a production-ready financial accounting API that implements **double-entry bookkeeping** principles with full validation, reporting, and Excel export capabilities. Built with modern Python technologies, it provides a solid foundation for fintech applications, ERP systems, and accounting software.

### Key Highlights

| Feature | Description |
|---------|-------------|
| **Double-Entry Validation** | Enforces `Total Debits = Total Credits` on every transaction |
| **Account Categories** | Asset, Liability, Equity, Income, Expense with normal balance logic |
| **Counterpart Management** | Customer, Supplier, Lender, Borrower relationship types |
| **Financial Reports** | Trial Balance, Account Ledger, Income Statement, Balance Sheet |
| **Excel Export** | One-click `.xlsx` workbook with all financial reports |
| **Database Migrations** | Alembic-powered schema versioning |
| **API Documentation** | Auto-generated Swagger/OpenAPI at `/docs` |

---

## Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CLIENT[API Client<br/>Swagger UI / Postman / cURL]
    end

    subgraph "API Layer"
        ROUTER[API Router]
        HEALTH[Health Routes]
        USER[User Routes]
        ACC[Account Routes]
        CP[Counterpart Routes]
        TXN[Transaction Routes]
        RPT[Report Routes]
    end

    subgraph "Service Layer"
        EXCEL[Excel Export Service]
        VALID[Validation Services]
        CALC[Calculation Services]
    end

    subgraph "Data Layer"
        MODELS[SQLAlchemy Models]
        SCHEMAS[Pydantic Schemas]
        SESSION[DB Session Manager]
        ALEMBIC[Alembic Migrations]
    end

    subgraph "Infrastructure"
        PG[(PostgreSQL)]
        UVICORN[Uvicorn ASGI Server]
    end

    CLIENT --> ROUTER
    ROUTER --> HEALTH
    ROUTER --> USER
    ROUTER --> ACC
    ROUTER --> CP
    ROUTER --> TXN
    ROUTER --> RPT

    USER --> VALID
    ACC --> VALID
    CP --> VALID
    TXN --> VALID
    TXN --> CALC
    RPT --> CALC
    RPT --> EXCEL

    VALID --> MODELS
    CALC --> MODELS
    EXCEL --> MODELS

    MODELS --> SESSION
    SCHEMAS --> MODELS
    SESSION --> PG
    ALEMBIC --> PG

    UVICORN --> ROUTER
```

---

## Quick Start

### Prerequisites

- **Python** 3.11+
- **PostgreSQL** 15+
- **Docker** (optional, for containerized deployment)

### Option 1: Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/DualEntry.git
cd DualEntry

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Run database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API available at:** `http://localhost:8000`  
**Interactive docs:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

### Option 2: Docker Deployment

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Stop services
docker-compose down
```

**docker-compose.yml included** with PostgreSQL, API, and optional pgAdmin.

---

## Installation

### Requirements

```text
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
alembic>=1.13.0
python-dotenv>=1.0.0

# Reports
openpyxl>=3.1.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
ruff>=0.1.0
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# Application
APP_NAME=DualEntry
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dualentry
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security (for future auth)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Transaction Flow

```mermaid
flowchart TD
    START([Create Transaction Request]) --> VALIDATE_USER{User Exists?}
    VALIDATE_USER -->|No| ERROR_USER[404 User Not Found]
    VALIDATE_USER -->|Yes| VALIDATE_CP{Counterpart Valid?}
    
    VALIDATE_CP -->|No| ERROR_CP[400 Invalid Counterpart]
    VALIDATE_CP -->|Yes| VALIDATE_ACCOUNTS{Accounts Valid & Owned?}
    
    VALIDATE_ACCOUNTS -->|No| ERROR_ACC[400 Account Error]
    VALIDATE_ACCOUNTS -->|Yes| VALIDATE_ENTRIES{Entries Valid?}
    
    VALIDATE_ENTRIES -->|Missing DEBIT/CREDIT| ERROR_ENTRY[400 Entry Error]
    VALIDATE_ENTRIES -->|Amounts ≤ 0| ERROR_AMT[400 Amount Error]
    VALIDATE_ENTRIES -->|Debits ≠ Credits| ERROR_BALANCE[400 Unbalanced]
    
    VALIDATE_ENTRIES -->|All Valid| CHECK_TYPE{Type-Specific Rules?}
    
    CHECK_TYPE -->|SALE/PURCHASE/EXPENSE/INCOME| VALIDATE_CATEGORY{Category Rules Match?}
    VALIDATE_CATEGORY -->|No| ERROR_CAT[400 Category Mismatch]
    VALIDATE_CATEGORY -->|Yes| PERSIST
    
    CHECK_TYPE -->|Other Types| PERSIST
    
    PERSIST[Save Transaction & Entries] --> UPDATE_BALANCES[Update Account Balances]
    UPDATE_BALANCES --> SUCCESS[201 Created + Transaction ID]
    
    ERROR_USER --> END([Error Response])
    ERROR_CP --> END
    ERROR_ACC --> END
    ERROR_ENTRY --> END
    ERROR_AMT --> END
    ERROR_BALANCE --> END
    ERROR_CAT --> END
    SUCCESS --> END
```

---

## Account Categories & Normal Balances

```mermaid
graph LR
    subgraph "DEBIT Normal Balance"
        ASSET[Asset<br/>💰]
        EXPENSE[Expense<br/>💸]
    end
    
    subgraph "CREDIT Normal Balance"
        LIABILITY[Liability<br/>📋]
        EQUITY[Equity<br/>📊]
        INCOME[Income<br/>💵]
    end
    
    style ASSET fill:#e8f5e9,stroke:#2e7d32
    style EXPENSE fill:#e8f5e9,stroke:#2e7d32
    style LIABILITY fill:#fff3e0,stroke:#ef6c00
    style EQUITY fill:#fff3e0,stroke:#ef6c00
    style INCOME fill:#fff3e0,stroke:#ef6c00
```

| Category | Normal Balance | Increases With | Decreases With |
|----------|----------------|----------------|----------------|
| **Asset** | Debit | Debit | Credit |
| **Expense** | Debit | Debit | Credit |
| **Liability** | Credit | Credit | Debit |
| **Equity** | Credit | Credit | Debit |
| **Income** | Credit | Credit | Debit |

---

## Transaction Types & Validation Rules

```mermaid
graph TD
    TXN_TYPE[Transaction Type] --> SALE[SALE]
    TXN_TYPE --> PURCHASE[PURCHASE]
    TXN_TYPE --> EXPENSE[EXPENSE]
    TXN_TYPE --> INCOME[INCOME]
    TXN_TYPE --> LOAN_R[LOAN_RECEIVED]
    TXN_TYPE --> LOAN_G[LOAN_GIVEN]
    TXN_TYPE --> LOAN_REPAY[LOAN_REPAYMENT]
    TXN_TYPE --> RECEIPT[RECEIPT]
    TXN_TYPE --> PAYMENT[PAYMENT]
    TXN_TYPE --> TRANSFER[TRANSFER]

    SALE --> RULE1[Debit: Asset<br/>Credit: Income]
    PURCHASE --> RULE2[Debit: Asset/Expense<br/>Credit: Asset/Liability]
    EXPENSE --> RULE3[Debit: Expense<br/>Credit: Asset/Liability]
    INCOME --> RULE4[Debit: Asset<br/>Credit: Income]
    
    LOAN_R --> FLEXIBLE[Flexible Account Categories]
    LOAN_G --> FLEXIBLE
    LOAN_REPAY --> FLEXIBLE
    RECEIPT --> FLEXIBLE
    PAYMENT --> FLEXIBLE
    TRANSFER --> FLEXIBLE
```

---

## API Endpoints

<details>
<summary><strong>📋 Click to expand all endpoints</strong></summary>

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health check |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/{user_id}` | Get user by ID |

### Accounts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/accounts/` | Create a new account |
| `GET` | `/accounts/{account_id}/balance` | Get account balance |
| `GET` | `/accounts/{account_id}/entries` | Get account journal entries |

### Counterparts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/counterparts/` | Create counterpart relationship |
| `GET` | `/counterparts/user/{user_id}` | List counterparts (filterable by type) |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions/` | Create a new transaction |
| `GET` | `/transactions/user/{user_id}` | List user transactions |
| `GET` | `/transactions/{transaction_id}` | Get transaction details |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports/trial-balance/{user_id}` | Trial balance report |
| `GET` | `/reports/account-ledger/{account_id}` | Account ledger with running balance |
| `GET` | `/reports/income-statement/{user_id}` | Income statement |
| `GET` | `/reports/balance-sheet/{user_id}` | Balance sheet |
| `GET` | `/reports/export/{user_id}` | **Excel export** (all reports) |

</details>

---

## Example Usage

### Create a Transaction (Cash Sale)

```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "counterpart_id": 2,
    "transaction_type": "SALE",
    "description": "Cash sale of services",
    "entries": [
      {"account_id": 3, "entry_type": "DEBIT", "amount": 5000.00},
      {"account_id": 5, "entry_type": "CREDIT", "amount": 5000.00}
    ]
  }'
```

**Response:**
```json
{
  "id": 10,
  "user_id": 1,
  "counterpart_id": 2,
  "transaction_type": "SALE",
  "description": "Cash sale of services",
  "created_at": "2026-01-15T10:30:00Z",
  "entries": [
    {"id": 19, "account_id": 3, "entry_type": "DEBIT", "amount": "5000.00"},
    {"id": 20, "account_id": 5, "entry_type": "CREDIT", "amount": "5000.00"}
  ]
}
```

### Get Financial Reports

```bash
# Trial Balance
curl "http://localhost:8000/reports/trial-balance/1"

# Income Statement
curl "http://localhost:8000/reports/income-statement/1"

# Balance Sheet
curl "http://localhost:8000/reports/balance-sheet/1"

# Excel Export (downloads .xlsx file)
curl -o financial_report.xlsx "http://localhost:8000/reports/export/1"
```

---

## Financial Reports

### Trial Balance
Verifies `Total Debits = Total Credits` across all accounts.

### Account Ledger
Shows individual entries with **running balance** per account.

### Income Statement
```
Revenue (Income)     150,000
Cost of Goods Sold   -45,000
Gross Profit          105,000
Operating Expenses   -30,000
Net Income             75,000
```

### Balance Sheet
```
ASSETS                          LIABILITIES & EQUITY
Cash              100,000       Accounts Payable    25,000
Accounts Receivable  50,000     Loans Payable       50,000
Inventory              30,000     Equity             105,000
─────────────────────           ─────────────────────
Total Assets        180,000     Total L&E           180,000
```

---

## Project Structure

```
DualEntry/
├── app/
│   ├── api/
│   │   ├── router.py
│   │   └── routes/
│   │       ├── account.py
│   │       ├── counterpart.py
│   │       ├── health.py
│   │       ├── report.py
│   │       ├── transaction.py
│   │       └── user.py
│   ├── database/
│   │   ├── base.py
│   │   ├── dependency.py
│   │   └── session.py
│   ├── models/
│   │   ├── account.py
│   │   ├── counterpart.py
│   │   ├── entry.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── account.py
│   │   ├── counterpart.py
│   │   ├── report.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── services/
│   │   └── excel_export.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Roadmap

### Phase 1: Core Stability ✅
- [x] Double-entry transaction engine
- [x] Account management & balance tracking
- [x] Counterpart relationships
- [x] Financial report generation
- [x] Excel export
- [x] Database migrations

### Phase 2: Security & Access Control 🔄
- [ ] JWT-based authentication
- [ ] Role-based access control (Admin, Accountant, Viewer)
- [ ] User-scoped data isolation
- [ ] API rate limiting
- [ ] Audit logging

### Phase 3: Enhanced Reporting 📊
- [ ] Date-range filtering for all reports
- [ ] Comparative reports (YoY, QoQ, MoM)
- [ ] Cash flow statement
- [ ] Custom report builder
- [ ] PDF export support
- [ ] Scheduled report generation

### Phase 4: Operational Excellence 🚀
- [ ] Comprehensive test suite (unit, integration, e2e)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Docker multi-stage builds
- [ ] Kubernetes deployment manifests
- [ ] Observability (Prometheus, Grafana, structured logging)
- [ ] Database connection pooling optimization

### Phase 5: Advanced Features ✨
- [ ] Multi-currency support
- [ ] Recurring transactions
- [ ] Budget vs. actuals
- [ ] Tax calculation engine
- [ ] Bank reconciliation
- [ ] Webhook notifications
- [ ] API versioning strategy

---

## Contributing

```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes with tests
# 4. Run quality checks
ruff check .
ruff format .
pytest

# 5. Commit with conventional commits
git commit -m "feat: add amazing feature"

# 6. Push and open a Pull Request
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation:** `/docs` endpoint when running locally
- **Issues:** [GitHub Issues](https://github.com/yourusername/DualEntry/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/DualEntry/discussions)

---

<p align="center">
  Made with ❤️ for accurate financial accounting
</p>