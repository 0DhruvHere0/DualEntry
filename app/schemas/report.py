from decimal import Decimal
from pydantic import BaseModel
class IncomeStatementItem(BaseModel):
    account_id: int
    account_name: str
    amount: Decimal
class IncomeStatementResponse(BaseModel):
    income: list[IncomeStatementItem]
    expenses: list[IncomeStatementItem]
    total_income: Decimal
    total_expenses: Decimal
    net_income: Decimal
class BalanceSheetItem(BaseModel):
    account_id: int | None
    account_name: str
    amount: Decimal
class BalanceSheetResponse(BaseModel):
    assets: list[BalanceSheetItem]
    liabilities: list[BalanceSheetItem]
    equity: list[BalanceSheetItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    total_liabilities_and_equity: Decimal