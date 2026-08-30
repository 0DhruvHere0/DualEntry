def test_create_sale_transaction(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    sales_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Sales Revenue",
            "category": "Income"
        }
    )
    sales_account_id = sales_response.json()["id"]
    counterpart_relationship = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert counterpart_relationship.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sold goods for cash",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": sales_account_id,
                    "entry_type": "CREDIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["transaction_type"] == "SALE"
    assert data["description"] == "Sold goods for cash"
    assert len(data["entries"]) == 2
    assert data["entries"][0]["account_id"] == cash_account_id
    assert data["entries"][0]["entry_type"] == "DEBIT"
    assert data["entries"][0]["amount"] == "1000.00"
    assert data["entries"][1]["account_id"] == sales_account_id
    assert data["entries"][1]["entry_type"] == "CREDIT"
    assert data["entries"][1]["amount"] == "1000.00"
def test_transaction_debits_must_equal_credits(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    sales_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Sales Revenue",
            "category": "Income"
        }
    )
    sales_account_id = sales_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Unbalanced sale",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": sales_account_id,
                    "entry_type": "CREDIT",
                    "amount": "900.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Total debits must equal total credits"
    )
def test_transaction_requires_debit_and_credit(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]
    account_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    account_id = account_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Debit only transaction",
            "entries": [
                {
                    "account_id": account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Transaction must contain both debit and credit entries"
    )
def test_transaction_requires_entries(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Empty transaction",
            "entries": []
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Transaction must contain at least one entry"
    )
def test_transaction_account_does_not_belong_to_user(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    other_user_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    other_user_id = other_user_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": other_user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Customer"}
    )
    counterpart_id = counterpart_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Invalid account ownership",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == (
        f"Account {cash_account_id} does not belong to this user"
    )
def test_transaction_cannot_be_with_same_user(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    sales_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Sales Revenue",
            "category": "Income"
        }
    )
    sales_account_id = sales_response.json()["id"]
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": user_id,
            "transaction_type": "SALE",
            "description": "Self transaction",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": sales_account_id,
                    "entry_type": "CREDIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "User and counterpart cannot be the same"
    )
def test_transaction_requires_counterpart_relationship(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Customer"}
    )
    counterpart_id = counterpart_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    sales_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Sales Revenue",
            "category": "Income"
        }
    )
    sales_account_id = sales_response.json()["id"]
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sale without relationship",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": sales_account_id,
                    "entry_type": "CREDIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Counterpart relationship does not exist"
    )
def test_loan_received_requires_lender_relationship(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Payable",
            "category": "Liability"
        }
    )
    loan_account_id = loan_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "LOAN_RECEIVED",
            "description": "Received loan from Rahul",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "LOAN_RECEIVED requires counterpart relationship to be LENDER"
    )
def test_create_loan_received_transaction(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    lender_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    lender_id = lender_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Payable",
            "category": "Liability"
        }
    )
    loan_account_id = loan_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "relationship_type": "LENDER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "transaction_type": "LOAN_RECEIVED",
            "description": "Received loan from Rahul",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["counterpart_id"] == lender_id
    assert data["transaction_type"] == "LOAN_RECEIVED"
    assert data["description"] == "Received loan from Rahul"
    assert len(data["entries"]) == 2
    assert data["entries"][0]["account_id"] == cash_account_id
    assert data["entries"][0]["entry_type"] == "DEBIT"
    assert data["entries"][0]["amount"] == "5000.00"
    assert data["entries"][1]["account_id"] == loan_account_id
    assert data["entries"][1]["entry_type"] == "CREDIT"
    assert data["entries"][1]["amount"] == "5000.00"
def test_loan_given_requires_borrower_relationship(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": loan_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
def test_create_loan_given_transaction(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": loan_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["counterpart_id"] == borrower_id
    assert data["transaction_type"] == "LOAN_GIVEN"
    assert data["description"] == "Gave loan to Rahul"
    assert len(data["entries"]) == 2
    assert data["entries"][0]["account_id"] == loan_account_id
    assert data["entries"][0]["entry_type"] == "DEBIT"
    assert data["entries"][0]["amount"] == "5000.00"
    assert data["entries"][1]["account_id"] == cash_account_id
    assert data["entries"][1]["entry_type"] == "CREDIT"
    assert data["entries"][1]["amount"] == "5000.00"
def test_loan_given_updates_account_balances(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201
    transaction_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": loan_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert transaction_response.status_code == 200
    cash_balance_response = client.get(
        f"/accounts/{cash_account_id}/balance"
    )
    assert cash_balance_response.status_code == 200
    cash_data = cash_balance_response.json()
    assert cash_data["balance"] == "-5000.00"
    loan_balance_response = client.get(
        f"/accounts/{loan_account_id}/balance"
    )
    assert loan_balance_response.status_code == 200
    loan_data = loan_balance_response.json()
    assert loan_data["balance"] == "5000.00"
def test_loan_repayment_requires_borrower_relationship(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]
    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]
    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]
    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]
    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201
    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid part of the loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert "BORROWER" in response.json()["detail"]
def test_create_loan_repayment_transaction(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid part of the loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["counterpart_id"] == borrower_id
    assert data["transaction_type"] == "LOAN_REPAYMENT"
    assert data["description"] == "Rahul repaid part of the loan"
    assert len(data["entries"]) == 2

    assert data["entries"][0]["account_id"] == cash_account_id
    assert data["entries"][0]["entry_type"] == "DEBIT"
    assert data["entries"][0]["amount"] == "2000.00"

    assert data["entries"][1]["account_id"] == loan_account_id
    assert data["entries"][1]["entry_type"] == "CREDIT"
    assert data["entries"][1]["amount"] == "2000.00"
def test_loan_repayment_updates_account_balances(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid part of the loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )

    assert response.status_code == 200

    cash_balance_response = client.get(
        f"/accounts/{cash_account_id}/balance"
    )
    assert cash_balance_response.status_code == 200

    cash_balance = cash_balance_response.json()

    loan_balance_response = client.get(
        f"/accounts/{loan_account_id}/balance"
    )
    assert loan_balance_response.status_code == 200

    loan_balance = loan_balance_response.json()

    assert cash_balance["balance"] == "2000.00"
    assert loan_balance["balance"] == "-2000.00"
def test_loan_repayment_cannot_exceed_outstanding_loan(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    # First, Rahul borrows ₹5,000
    loan_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": loan_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert loan_response.status_code == 200

    # Rahul tries to repay ₹6,000
    repayment_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "6000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "6000.00"
                }
            ]
        }
    )

    assert repayment_response.status_code == 400
def test_loan_received_requires_correct_account_categories(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    lender_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    lender_id = lender_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    liability_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Payable",
            "category": "Liability"
        }
    )
    liability_account_id = liability_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "relationship_type": "LENDER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": lender_id,
            "transaction_type": "LOAN_RECEIVED",
            "description": "Received loan from Rahul",
            "entries": [
                {
                    "account_id": liability_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )

    assert response.status_code == 400


def test_loan_given_requires_correct_account_categories(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    income_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Income",
            "category": "Income"
        }
    )
    income_account_id = income_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": income_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )

    assert response.status_code == 400


def test_loan_repayment_requires_correct_account_categories(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    expense_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Expense",
            "category": "Expense"
        }
    )
    expense_account_id = expense_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": expense_account_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )

    assert response.status_code == 200


def test_loan_repayment_with_non_loan_account_does_not_reduce_loan(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    other_asset_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Other Asset",
            "category": "Asset"
        }
    )
    other_asset_id = other_asset_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repayment",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": other_asset_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )

    assert response.status_code == 200


def test_partial_loan_repayment_respects_remaining_balance(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    borrower_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    borrower_id = borrower_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    loan_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Loan Receivable",
            "category": "Asset"
        }
    )
    loan_account_id = loan_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "relationship_type": "BORROWER"
        }
    )
    assert relationship_response.status_code == 201

    loan_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_GIVEN",
            "description": "Gave loan to Rahul",
            "entries": [
                {
                    "account_id": loan_account_id,
                    "entry_type": "DEBIT",
                    "amount": "5000.00"
                },
                {
                    "account_id": cash_account_id,
                    "entry_type": "CREDIT",
                    "amount": "5000.00"
                }
            ]
        }
    )
    assert loan_response.status_code == 200

    repayment_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid part of loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "2000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "2000.00"
                }
            ]
        }
    )

    assert repayment_response.status_code == 200

    second_repayment_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": borrower_id,
            "transaction_type": "LOAN_REPAYMENT",
            "description": "Rahul repaid remaining loan",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "3000.00"
                },
                {
                    "account_id": loan_account_id,
                    "entry_type": "CREDIT",
                    "amount": "3000.00"
                }
            ]
        }
    )

    assert second_repayment_response.status_code == 200


def test_transaction_rejects_nonexistent_account(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    counterpart_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    counterpart_id = counterpart_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201

    response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Invalid transaction",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": 999999,
                    "entry_type": "CREDIT",
                    "amount": "1000.00"
                }
            ]
        }
    )

    assert response.status_code == 404


def test_multiple_transactions_preserve_account_balance(client):
    user_response = client.post(
        "/users/",
        json={"name": "Dhruv"}
    )
    user_id = user_response.json()["id"]

    customer_response = client.post(
        "/users/",
        json={"name": "Rahul"}
    )
    customer_id = customer_response.json()["id"]

    cash_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    cash_account_id = cash_response.json()["id"]

    income_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Sales",
            "category": "Income"
        }
    )
    income_account_id = income_response.json()["id"]

    relationship_response = client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": customer_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code == 201

    sale_one = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": customer_id,
            "transaction_type": "SALE",
            "description": "First sale",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1000.00"
                },
                {
                    "account_id": income_account_id,
                    "entry_type": "CREDIT",
                    "amount": "1000.00"
                }
            ]
        }
    )
    assert sale_one.status_code == 200

    sale_two = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": customer_id,
            "transaction_type": "SALE",
            "description": "Second sale",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "1500.00"
                },
                {
                    "account_id": income_account_id,
                    "entry_type": "CREDIT",
                    "amount": "1500.00"
                }
            ]
        }
    )
    assert sale_two.status_code == 200

    balance_response = client.get(
        f"/accounts/{cash_account_id}/balance"
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == "2500.00"