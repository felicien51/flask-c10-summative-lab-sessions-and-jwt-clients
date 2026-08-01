# TaskFlow API — Session-Auth Productivity Backend

## Project Description

TaskFlow is a secure RESTful Flask API that powers a personal task-tracking
productivity app. It implements full **cookie/session-based authentication**
(sign up, log in, log out, and session persistence via `check_session`) and
exposes a **user-owned `Task` resource** with complete CRUD, ownership
enforcement, and pagination.

It is designed to work with the `client-with-sessions` React frontend
included in this repository — no frontend code was written as part of this
lab, but every endpoint the client expects (`/signup`, `/login`, `/logout`,
`/check_session`) is implemented and returns the exact shapes the client
consumes.

### Features

- Secure password storage with **bcrypt** (`flask-bcrypt`) — plaintext
  passwords are never stored or returned.
- **Unique, validated usernames** enforced at both the model and database
  level.
- Session-based auth using Flask's signed cookie session (`session['user_id']`).
- A `Task` model owned by `User` (one-to-many) with four custom fields:
  `description`, `priority`, `completed`, and `due_date` (in addition to
  `title`).
- Full CRUD for tasks: `GET`, `POST`, `PATCH`, `DELETE`.
- **Ownership protection** — a logged-in user can only view, edit, or delete
  their own tasks; attempting to access another user's task returns `404`.
- **Pagination** on the tasks index route via `?page=` and `?per_page=` query
  params.
- Marshmallow-based request validation with clear `422` error payloads.
- `seed.py` populates the database with demo users and randomized tasks
  (via `Faker`).
- Automated test suite (`pytest`) covering auth flow, CRUD, ownership, and
  pagination.

---

## Tech Stack

- Python 3.11 / Flask 2.2.2
- Flask-SQLAlchemy 3.0.3 + Flask-Migrate 4.0.0 (SQLite by default)
- Flask-RESTful 0.3.9
- Flask-Bcrypt 1.0.1
- Marshmallow 3.20.1
- Faker 15.3.2 (seeding)
- Pytest 7.2.0 (testing)

---

## Installation

From the `server/` directory:

```bash
pipenv install
pipenv shell
```

> Prefer plain `pip`? You can instead do:
> ```bash
> python3 -m venv venv
> source venv/bin/activate   # Windows: venv\Scripts\activate
> pip install flask==2.2.2 flask-sqlalchemy==3.0.3 werkzeug==2.2.2 \
>     marshmallow==3.20.1 faker==15.3.2 flask-migrate==4.0.0 \
>     flask-restful==0.3.9 flask-bcrypt==1.0.1 flask-cors pytest
> ```

### Set up the database

```bash
export FLASK_APP=app.py        # Windows (cmd): set FLASK_APP=app.py
flask db init                  # only needed the first time (migrations/ folder already included)
flask db upgrade
python seed.py
```

This creates `app.db` (SQLite) with 5 demo users (including a predictable
`demo` / `password123` account) and several randomized tasks per user.

---

## Running the App

```bash
export FLASK_APP=app.py
flask run --port 5555
```

or simply:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5555`.

To use it with the provided frontend, run the `client-with-sessions` React
app (`npm install && npm start`) — its dev server proxies API requests to
port 5555.

### Running Tests

```bash
pytest -v
```

---

## Endpoints

### Auth

| Method | Route            | Description                                                                 | Auth required |
|--------|------------------|-------------------------------------------------------------------------------|:---:|
| POST   | `/signup`        | Create a new user. Body: `{ username, password, password_confirmation }`. Logs the user in (sets session) and returns the user. `201` on success, `422` on validation errors (duplicate username, mismatched passwords, etc). | No |
| POST   | `/login`         | Authenticate a user. Body: `{ username, password }`. Returns the user and sets the session cookie. `200` on success, `401` on invalid credentials. | No |
| DELETE | `/logout`        | Clears the current session. `204` on success, `401` if no user was logged in. | Yes |
| GET    | `/check_session` | Returns the currently logged-in user (used on app load / refresh to restore session). `200` if logged in, `401` otherwise. | Yes |

### Tasks (user-owned resource)

| Method | Route          | Description                                                                                     | Auth required |
|--------|----------------|---------------------------------------------------------------------------------------------------|:---:|
| GET    | `/tasks`       | Returns a **paginated** list of the current user's tasks only. Query params: `page` (default `1`), `per_page` (default `10`, max `100`). Response: `{ tasks: [...], meta: { page, per_page, total, total_pages, has_next, has_prev } }`. | Yes |
| POST   | `/tasks`       | Create a new task owned by the current user. Body: `{ title, description?, priority?, completed?, due_date? }`. `201` on success, `422` on validation errors. | Yes |
| GET    | `/tasks/<id>`  | Return a single task. `404` if the task doesn't exist or isn't owned by the current user.       | Yes |
| PATCH  | `/tasks/<id>`  | Partially update a task (any subset of `title`, `description`, `priority`, `completed`, `due_date`). `404` if not owned by the current user, `422` on validation errors. | Yes |
| DELETE | `/tasks/<id>`  | Delete a task. `204` on success, `404` if not owned by the current user.                        | Yes |

**Task fields:** `id`, `title`, `description`, `priority` (`low` / `medium` /
`high`), `completed` (bool), `due_date` (`YYYY-MM-DD`), `created_at`,
`updated_at`, `user_id`.

**Demo credentials (after seeding):** `username: demo`, `password: password123`

---

## Project Structure

```
server/
├── app.py                 # Entry point — registers routes, runs the dev server
├── config.py               # Flask app, SQLAlchemy, Migrate, Bcrypt, Api, CORS setup
├── models.py                # User and Task SQLAlchemy models
├── schemas.py                # Marshmallow request-validation schemas
├── decorators.py              # @login_required auth decorator
├── resources/
│   ├── auth.py                 # SignUp, Login, Logout, CheckSession
│   └── tasks.py                 # TaskList (index/create + pagination), TaskDetail (show/update/delete)
├── seed.py                  # Database seeding script
├── migrations/                # Flask-Migrate/Alembic migrations
├── tests/
│   ├── conftest.py             # Pytest fixtures (in-memory test DB)
│   └── test_app.py              # Auth + Task endpoint test suite
├── Pipfile
└── README.md
```
