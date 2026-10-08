def register(client, username="alice", password="securepass1"):
    return client.post("/auth/register", json={"username": username, "password": password})


def login(client, username="alice", password="securepass1"):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_register_login_validate_and_refresh_token(client):
    registration = register(client)
    assert registration.status_code == 201
    assert registration.json()["username"] == "alice"
    assert "hashed_password" not in registration.json()

    logged_in = login(client)
    assert logged_in.status_code == 200
    token_response = logged_in.json()
    assert token_response["token_type"] == "bearer"
    assert token_response["expires_in"] == 3600
    original_token = token_response["access_token"]

    original_headers = {"Authorization": f"Bearer {original_token}"}
    assert client.post("/auth/validate", headers=original_headers).json()["valid"]

    refreshed = client.post("/auth/refresh", headers=original_headers)
    assert refreshed.status_code == 200
    refreshed_token = refreshed.json()["access_token"]
    assert refreshed_token != original_token
    assert client.post("/auth/validate", headers=original_headers).status_code == 401
    assert client.post(
        "/auth/validate", headers={"Authorization": f"Bearer {refreshed_token}"}
    ).status_code == 200
    assert client.post("/auth/refresh", headers=original_headers).status_code == 401


def test_registration_rejects_duplicate_username_case_insensitively(client):
    assert register(client).status_code == 201

    duplicate = register(client, username="ALICE")

    assert duplicate.status_code == 409


def test_login_rejects_unknown_user_and_wrong_password(client):
    assert login(client).status_code == 401
    assert register(client).status_code == 201
    assert login(client, password="wrongpass1").status_code == 401


def test_registration_enforces_input_boundaries(client):
    assert register(client, username="abc", password="12345678").status_code == 201
    assert register(client, username="u" * 50, password="p" * 128).status_code == 201
    assert register(client, username="ab", password="12345678").status_code == 422
    assert register(client, username="alice", password="short").status_code == 422
    assert register(client, username="u" * 51, password="12345678").status_code == 422
    assert register(client, username="bob", password="p" * 129).status_code == 422


def test_validate_and_refresh_reject_missing_or_invalid_tokens(client):
    assert client.post("/auth/validate").status_code == 401
    assert client.post("/auth/refresh").status_code == 401
    invalid_headers = {"Authorization": "Bearer invalid-token"}
    assert client.post("/auth/validate", headers=invalid_headers).status_code == 401
    assert client.post("/auth/refresh", headers=invalid_headers).status_code == 401