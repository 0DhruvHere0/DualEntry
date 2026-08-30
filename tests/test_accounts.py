def test_create_account(client):
    user_response = client.post(
        "/users/",
        json={
            "name": "Account Owner"
        }
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]
    response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["name"] == "Cash"
    assert data["category"] == "Asset"
    assert "id" in data
    assert "created_at" in data
def test_get_account_balance(client):
    user_response = client.post(
        "/users/",
        json={
            "name": "Dhruv"
        }
    )
    user_id = user_response.json()["id"]
    account_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Cash",
            "category": "Asset"
        }
    )
    account_id = account_response.json()["id"]
    response = client.get(
        f"/accounts/{account_id}/balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
    assert data["account_name"] == "Cash"
    assert data["category"] == "Asset"
    assert data["balance"] == "0.00"
def test_get_account_balance_with_entries(client):
    user_response = client.post(
        "/users/",
        json={
            "name": "Dhruv"
        }
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
            "name": "Sales",
            "category": "Income"
        }
    )
    sales_account_id = sales_response.json()["id"]
    counterpart_response = client.post(
        "/users/",
        json={
            "name": "Customer"
        }
    )
    counterpart_id = counterpart_response.json()["id"]
    relationship_response= client.post(
        "/counterparts/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "relationship_type": "CUSTOMER"
        }
    )
    assert relationship_response.status_code==201
    transaction_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sale for cash",
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
    assert transaction_response.status_code == 200
    response = client.get(
        f"/accounts/{cash_account_id}/balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "1000.00"
def test_get_account_ledger(client):
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
    transaction_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sale for cash",
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
    assert transaction_response.status_code == 200
    ledger_response = client.get(
        f"/accounts/{cash_account_id}/ledger"
    )
    assert ledger_response.status_code == 200
    data = ledger_response.json()
    assert data["account_id"] == cash_account_id
    assert data["account_name"] == "Cash"
    assert data["category"] == "Asset"
    assert len(data["entries"]) == 1
    entry = data["entries"][0]
    assert entry["entry_type"] == "DEBIT"
    assert entry["amount"] == "1000.00"
    assert entry["debit"] == "1000.00"
    assert entry["credit"] == "0.00"
    assert entry["balance"] == "1000.00"
    assert entry["description"] == "Sale for cash"
    assert entry["transaction_type"] == "SALE"
def test_get_trial_balance(client):
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
    transaction_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sale for cash",
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
    assert transaction_response.status_code == 200
    response = client.get(
        f"/accounts/{user_id}/trial-balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["accounts"]) == 2
    assert data["total_debit"] == "1000.00"
    assert data["total_credit"] == "1000.00"
def test_trial_balance_aggregates_multiple_transactions(client):
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
    first_transaction = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "First sale",
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
    assert first_transaction.status_code == 200
    second_transaction = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Second sale",
            "entries": [
                {
                    "account_id": cash_account_id,
                    "entry_type": "DEBIT",
                    "amount": "500.00"
                },
                {
                    "account_id": sales_account_id,
                    "entry_type": "CREDIT",
                    "amount": "500.00"
                }
            ]
        }
    )
    assert second_transaction.status_code == 200
    response = client.get(
        f"/accounts/{user_id}/trial-balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_debit"] == "1500.00"
    assert data["total_credit"] == "1500.00"
    cash = next(
        account
        for account in data["accounts"]
        if account["account_id"] == cash_account_id
    )
    sales = next(
        account
        for account in data["accounts"]
        if account["account_id"] == sales_account_id
    )
    assert cash["debit"] == "1500.00"
    assert cash["credit"] == "0.00"
    assert sales["debit"] == "0.00"
    assert sales["credit"] == "1500.00"
def test_trial_balance_includes_accounts_with_no_entries(client):
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
    bank_response = client.post(
        "/accounts/",
        json={
            "user_id": user_id,
            "name": "Bank",
            "category": "Asset"
        }
    )
    bank_account_id = bank_response.json()["id"]
    response = client.get(
        f"/accounts/{user_id}/trial-balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["accounts"]) == 2
    cash = next(
        account
        for account in data["accounts"]
        if account["account_id"] == cash_account_id
    )
    bank = next(
        account
        for account in data["accounts"]
        if account["account_id"] == bank_account_id
    )
    assert cash["debit"] == "0.00"
    assert cash["credit"] == "0.00"
    assert bank["debit"] == "0.00"
    assert bank["credit"] == "0.00"
    assert data["total_debit"] == "0.00"
    assert data["total_credit"] == "0.00"
def test_trial_balance_debits_equal_credits(client):
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
    transaction_response = client.post(
        "/transactions/",
        json={
            "user_id": user_id,
            "counterpart_id": counterpart_id,
            "transaction_type": "SALE",
            "description": "Sale for cash",
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
    assert transaction_response.status_code == 200
    response = client.get(
        f"/accounts/{user_id}/trial-balance"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_debit"] == data["total_credit"]