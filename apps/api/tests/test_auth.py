def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_creates_company_workspace_and_admin_user(client):
    payload = {
        "company_name": "Acme Corp",
        "industry": "Software",
        "workspace_name": "Acme Workspace",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "+1234567890",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["email"] == payload["email"]


def test_duplicate_email_is_rejected(client):
    payload = {
        "company_name": "Acme Corp",
        "industry": "Software",
        "workspace_name": "Acme Workspace",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "duplicate@example.com",
        "phone": "+1234567890",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!",
    }

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 200

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_returns_tokens(client):
    register_payload = {
        "company_name": "Acme Corp",
        "industry": "Software",
        "workspace_name": "Acme Workspace",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "login@example.com",
        "phone": "+1234567890",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!",
    }
    client.post("/auth/register", json=register_payload)

    response = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_weak_password_is_rejected(client):
    payload = {
        "company_name": "Acme Corp",
        "industry": "Software",
        "workspace_name": "Acme Workspace",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "weak@example.com",
        "phone": "+1234567890",
        "password": "weak",
        "confirm_password": "weak",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
