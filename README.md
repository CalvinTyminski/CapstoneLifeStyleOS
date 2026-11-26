# Lifestyle OS

A full-stack lifestyle management application that combines personal goal tracking with a gamified virtual economy. Users create and complete goals, earn virtual coins, and spend those coins on items for a virtual city.

Developed as a three-person Computer Programming capstone project.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, JavaScript, Vite |
| Backend | Python, FastAPI, Pydantic |
| Database | PostgreSQL 17, SQLAlchemy, Psycopg 3 |
| Migrations | Alembic |
| Authentication | JWT, Argon2 password hashing |
| Development | Docker, Docker Compose, Git, GitHub |
| Testing | Pytest, FastAPI TestClient, PostgreSQL |

## Features

### Authentication
- User registration and login with JWT access tokens.
- Passwords securely hashed using Argon2.
- A zero-balance virtual wallet created when an account is registered.
- Authenticated API routes scoped to the current user.

### Goals and Rewards
- Create fitness, nutrition, and habit goals with start and optional end dates.
- Complete eligible goals to receive server-defined virtual coin rewards.
- Record goal completions and wallet rewards in the same database transaction.
- Prevent duplicate rewards for the same one-time goal.

### Virtual Wallet
- Check wallet balance and view transaction history.
- Add simulated funds through a mock-deposit endpoint.
- Track `DEPOSIT`, `REWARD`, and `PURCHASE` events in a transaction ledger.
- Use idempotency keys to avoid processing repeated deposit requests twice.

### Virtual Store
- Browse virtual items and their prices.
- Purchase items using wallet coins.
- Record wallet deductions, purchase details, and ledger debits atomically.
- Reject purchases with insufficient funds and prevent duplicate charges from retried requests.

**All currency is simulated; no real payments are processed.** Goal completion is self-reported in the current implementation.

## Application Flow

1. Register or log in.
2. Create a fitness, nutrition, or habit goal.
3. Complete the goal and receive virtual coins.
4. View the updated wallet balance and reward transaction.
5. Browse the store and purchase an item.
6. Review the purchase history and wallet ledger.

The React interface and visual city-upgrade experience are being integrated with the backend.

## Architecture

```text
React + Vite frontend
        |
        | REST / JSON + JWT
        v
FastAPI API routes
        |
        v
Services: authentication, goals, wallet, store
        |
        v
SQLAlchemy + Psycopg
        |
        v
PostgreSQL
```

The backend is responsible for authentication, validating requests, setting reward amounts, calculating purchase prices, and updating balances. PostgreSQL transactions ensure that related balance, ledger, completion, and purchase records are saved together or rolled back together.

**Transaction safeguards:**
- `SELECT ... FOR UPDATE` locks wallet rows during balance changes.
- Unique constraints and idempotency keys prevent duplicate processing.
- `NUMERIC(12,2)` and Python `Decimal` provide fixed-precision balances.
- Database constraints prevent negative wallet balances.

### Main Database Tables

`users`, `wallets`, `ledger_entries`, `goals`, `goal_completions`, `store_items`, `purchases`, `alembic_version`.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | API health check |
| `POST` | `/api/auth/register` | Register user and create wallet |
| `POST` | `/api/auth/login` | Log in and receive JWT |
| `GET` | `/api/auth/me` | Current user profile |
| `POST` | `/api/goals` | Create goal |
| `GET` | `/api/goals` | List user goals |
| `POST` | `/api/goals/{goal_id}/complete` | Complete goal and award coins |
| `GET` | `/api/wallet` | Current wallet balance |
| `POST` | `/api/wallet/mock-deposits` | Add simulated funds |
| `GET` | `/api/wallet/transactions` | Wallet transaction history |
| `GET` | `/api/store/items` | List available store items |
| `POST` | `/api/store/purchases` | Purchase item |
| `GET` | `/api/store/purchases` | Purchase history |

Protected endpoints require a bearer JWT. Deposit and purchase requests also require an `Idempotency-Key` header.

Interactive API documentation is available at **http://127.0.0.1:8000/docs** while the backend is running.

## Local Setup

### Prerequisites

- Git
- Python 3 with `venv` support
- Docker Desktop and Docker Compose
- Node.js and npm for the React frontend

### 1. Clone the repository

```bash
git clone https://github.com/CalvinTyminski/CapstoneLifeStyleOS.git
cd CapstoneLifeStyleOS
```

### 2. Start PostgreSQL

From the repository root:

```bash
docker compose up -d
docker compose ps
```

### 3. Configure the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

For Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` and copy the file using `Copy-Item .env.example .env`.

Set the required values in `backend/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://lifestyle:<LOCAL_PASSWORD>@localhost:5432/lifestyle_os
JWT_SECRET_KEY=<RANDOM_SECRET>
```

Use the PostgreSQL credentials configured in `docker-compose.yml`. Generate a JWT secret with `openssl rand -hex 32`. Never commit `.env`.

### 4. Apply migrations and seed store items

From `backend/`:

```bash
alembic upgrade head
python seed_store.py
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

### 6. Start the frontend

In another terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (typically **http://localhost:5173**). Frontend code may still reside on a separate development branch until integrated into `main`.

## Tests

Backend tests use a separate PostgreSQL database named `lifestyle_os_test`.

Create the database once, from the repository root:

```bash
docker compose exec db psql -U lifestyle -d postgres -c "CREATE DATABASE lifestyle_os_test;"
```

Then run tests from `backend/` with its virtual environment active:

```bash
python -m pytest -v
```

The test suite covers authentication, wallet deposits, idempotency, invalid requests, transaction rollback, concurrent deposits, store purchases, and one-time goal rewards. **Test fixtures reset data in the test database; never point them at a database containing important data.**

## Development Status

**Backend implemented and locally tested:** authentication, wallet and ledger, mock deposits, store purchases, goals, wallet rewards, database migrations, and integration tests.

**In progress:** complete React integration, visual city upgrades, expanded lifestyle tracking and achievements, additional store/reward concurrency tests, and cloud deployment.

## Team Development

This project is developed collaboratively using feature branches and GitHub pull requests. Changes should be tested and reviewed before merging into `main`.

## License

No license has been specified for this repository.
