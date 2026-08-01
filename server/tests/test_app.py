import json


def signup(client, username="user1", password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password,
        },
    )


def login(client, username="user1", password="password123"):
    return client.post("/login", json={"username": username, "password": password})


class TestAuth:
    def test_signup_creates_user_and_logs_in(self, client):
        resp = signup(client)
        assert resp.status_code == 201
        assert resp.json["username"] == "user1"
        assert "password" not in resp.json
        assert "_password_hash" not in resp.json

    def test_signup_requires_matching_passwords(self, client):
        resp = client.post(
            "/signup",
            json={
                "username": "user1",
                "password": "password123",
                "password_confirmation": "nope",
            },
        )
        assert resp.status_code == 422

    def test_signup_rejects_duplicate_username(self, client):
        signup(client)
        resp = signup(client)
        assert resp.status_code == 422

    def test_login_success(self, client):
        signup(client)
        client.delete("/logout")
        resp = login(client)
        assert resp.status_code == 200
        assert resp.json["username"] == "user1"

    def test_login_invalid_credentials(self, client):
        signup(client)
        resp = login(client, password="wrongpass")
        assert resp.status_code == 401

    def test_check_session_unauthenticated(self, client):
        resp = client.get("/check_session")
        assert resp.status_code == 401

    def test_check_session_authenticated(self, client):
        signup(client)
        resp = client.get("/check_session")
        assert resp.status_code == 200
        assert resp.json["username"] == "user1"

    def test_logout(self, client):
        signup(client)
        resp = client.delete("/logout")
        assert resp.status_code == 204
        resp = client.get("/check_session")
        assert resp.status_code == 401


class TestTasks:
    def test_requires_login_for_index(self, client):
        resp = client.get("/tasks")
        assert resp.status_code == 401

    def test_create_and_list_task(self, client):
        signup(client)
        resp = client.post(
            "/tasks", json={"title": "Buy groceries", "priority": "low"}
        )
        assert resp.status_code == 201
        assert resp.json["title"] == "Buy groceries"

        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json["meta"]["total"] == 1
        assert resp.json["tasks"][0]["title"] == "Buy groceries"

    def test_pagination(self, client):
        signup(client)
        for i in range(15):
            client.post("/tasks", json={"title": f"Task {i}"})

        resp = client.get("/tasks?page=2&per_page=10")
        assert resp.status_code == 200
        assert resp.json["meta"]["page"] == 2
        assert resp.json["meta"]["total"] == 15
        assert resp.json["meta"]["total_pages"] == 2
        assert len(resp.json["tasks"]) == 5

    def test_users_cannot_access_others_tasks(self, client):
        signup(client, "alice", "password123")
        resp = client.post("/tasks", json={"title": "Alice's task"})
        task_id = resp.json["id"]
        client.delete("/logout")

        signup(client, "bob", "password123")
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 404

        resp = client.patch(f"/tasks/{task_id}", json={"completed": True})
        assert resp.status_code == 404

        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 404

        resp = client.get("/tasks")
        assert resp.json["meta"]["total"] == 0

    def test_update_own_task(self, client):
        signup(client)
        resp = client.post("/tasks", json={"title": "Original"})
        task_id = resp.json["id"]

        resp = client.patch(f"/tasks/{task_id}", json={"title": "Updated", "completed": True})
        assert resp.status_code == 200
        assert resp.json["title"] == "Updated"
        assert resp.json["completed"] is True

    def test_delete_own_task(self, client):
        signup(client)
        resp = client.post("/tasks", json={"title": "To delete"})
        task_id = resp.json["id"]

        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 204

        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 404

    def test_create_task_validation_error(self, client):
        signup(client)
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422
