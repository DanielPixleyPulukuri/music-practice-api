# Music Practice API

A RESTful backend API for managing a personal music library and tracking practice sessions. Built with Python and FastAPI, the application allows authenticated users to organize songs, record musical details, and maintain a history of their practice sessions.

The project is designed around a practical use case: helping musicians organize songs by their original key, playing key, tempo, and personal notes while keeping track of their practice activities.

## Features

### User Authentication
- User registration with username, email, and password.
- Password hashing instead of storing plain-text passwords.
- Login using email and password.
- JWT-based access tokens for authenticated requests.
- Protected endpoints that identify the current user.

### Song Management
- Create, retrieve, update, and delete songs.
- Store song titles, original keys, playing keys, book numbers, BPM, and personal notes.
- Automatically use the original key as the playing key when a playing key is not provided during creation.
- Filter songs by title and original musical key.
- Sort songs by supported fields in ascending or descending order.
- Paginate song listings.
- Retrieve a song with its associated practice sessions.

### Practice Session Tracking
- Record practice sessions for songs in the user's library.
- Store the practice date, duration, and notes.
- Retrieve individual practice sessions or list sessions.
- Filter practice sessions by song.
- Sort and paginate practice-session results.
- Update or delete existing sessions.
- Prevent users from accessing another user's songs and associated practice sessions through the API.

### Database and Validation
- PostgreSQL for persistent data storage.
- SQLAlchemy ORM for database operations.
- Pydantic schemas for request validation and response serialization.
- Alembic for database schema migrations.
- Pytest for automated API testing.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Pydantic | Request validation and response schemas |
| SQLAlchemy | ORM and database operations |
| PostgreSQL | Relational database |
| Alembic | Database schema migrations |
| PyJWT | JWT token handling |
| pwdlib with Argon2 | Password hashing |
| pytest | Automated testing |
| Uvicorn | ASGI application server |

## Project Structure

The application follows a modular structure, separating API routes, database models, schemas, configuration, and authentication logic.

```text
music-practice-api/
├── alembic/
│   └── versions/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── enums.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── song.py
│   │   └── practice_session.py
│   ├── routers/
│   │   ├── user.py
│   │   ├── song.py
│   │   └── practice_session.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── song.py
│   │   └── practice_session.py
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_songs.py
│   └── test_practice_sessions.py
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

*The structure above describes the intended project layout. Ensure the files shown are present in your repository before publishing this tree.*

## Getting Started

### Prerequisites

Install the following:

- Python 3.11 or another Python version compatible with your dependencies.
- PostgreSQL.
- Git.
- A terminal or command-line interface.

### 1. Clone the Repository

```bash
git clone https://github.com/DanielPixleyPulukuri/music-practice-api.git
cd music-practice-api
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux or macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file in the project root. Do not commit this file or expose its secrets.

Configure the following variables:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/music_practice
TEST_DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/music_practice_test
SECRET_KEY=replace_with_a_secure_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the example credentials and database names with your local configuration. The example token expiration is 30 minutes; adjust it to match your application configuration.

Create both PostgreSQL databases before running the application and tests.

**Security notes:**
- Use a strong, randomly generated secret key.
- Never commit `.env` or real database credentials.
- Keep the test database separate from the development database.
- Do not use development secrets in a production environment.

### 5. Apply Database Migrations

After configuring the database, apply the Alembic migrations:

```bash
alembic upgrade head
```

This applies the database schema defined by the migration files.

When you change your SQLAlchemy models, review the generated migration before applying it. Do not assume every autogenerated migration is correct.

### 6. Start the API Server

Run the application from the project root:

```bash
python -m uvicorn app.main:app --reload
```

The development server will normally be available at:

```text
http://127.0.0.1:8000
```

### 7. Explore the API Documentation

FastAPI generates interactive API documentation automatically.

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

Use Swagger UI to inspect endpoints, submit requests, and test authenticated operations.

## API Endpoints

The following endpoints are available in the current application routes.

### Users

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/users/register` | Register a new user | Not required |
| POST | `/users/login` | Authenticate and obtain an access token | Not required |
| GET | `/users/me` | Retrieve the authenticated user's profile | Required |

### Songs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/songs/` | Create a song |
| GET | `/songs/` | List songs with filtering, sorting, and pagination |
| GET | `/songs/{song_id}` | Retrieve a specific song |
| PATCH | `/songs/{song_id}` | Update a song |
| DELETE | `/songs/{song_id}` | Delete a song |
| GET | `/songs/{song_id}/details` | Retrieve a song with its associated practice-session details |
| GET | `/songs/{song_id}/practice-sessions` | Retrieve practice sessions for a song |

All song endpoints require authentication and operate within the authenticated user's song collection.

The song listing supports query parameters including `skip`, `limit`, `title`, `original_key`, `sort_by`, and `order`.

### Practice Sessions

| Method | Endpoint | Description |
|---|---|---|
| POST | `/practice-sessions/` | Create a practice session |
| GET | `/practice-sessions/` | List practice sessions |
| GET | `/practice-sessions/{practice_id}` | Retrieve a specific practice session |
| PATCH | `/practice-sessions/{practice_id}` | Update a practice session |
| DELETE | `/practice-sessions/{practice_id}` | Delete a practice session |

Practice-session endpoints require authentication. Sessions are associated with songs, and access is restricted to the authenticated user's songs.

The listing supports query parameters including `skip`, `limit`, `song_id`, `sort_by`, and `order`.

For exact request and response schemas, refer to the generated Swagger documentation.

## Authentication Flow

The API uses JWT bearer authentication.

1. Register a user through `POST /users/register`.
2. Log in through `POST /users/login`.
3. Copy the returned `access_token`.
4. In Swagger UI, click **Authorize** and enter the token as a bearer token if prompted.
5. Use the protected endpoints.

Example login response:

```json
{
  "access_token": "<your_access_token>",
  "token_type": "bearer"
}
```

Protected requests use the following HTTP header:

```http
Authorization: Bearer <your_access_token>
```

Passwords are hashed before being stored. Protected song and practice-session operations check ownership to prevent users from accessing other users' data through those endpoints.

## Running Tests

The project includes automated tests for user authentication, song operations, practice-session operations, and access control.

Ensure that `TEST_DATABASE_URL` points to a dedicated test database and that the test environment is configured correctly.

Run the test suite from the project root:

```bash
python -m pytest -v
```

The tests use FastAPI's test client and a separate SQLAlchemy database session configured for testing.

**Important:** The test setup creates and drops database tables. Never point `TEST_DATABASE_URL` at a database containing data you need to preserve.

## Database Migrations

Alembic manages schema changes independently of the application code.

Apply existing migrations:

```bash
alembic upgrade head
```

Check the current migration revision:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

When a model change requires a schema update, generate a migration, review it, and then apply it.

## Current Scope and Future Improvements

The current project focuses on the core backend functionality: authentication, song management, practice-session tracking, database persistence, and automated testing.

Potential future improvements include:

- Docker and Docker Compose for running the API and PostgreSQL together.
- Deployment to a hosting platform.
- Continuous integration for automated test execution.
- Improved validation for update requests and additional edge cases.
- Additional filtering and reporting for practice history.
- Import and export of a user's song library.

These are potential improvements, not claims about features already implemented.

## Purpose

This project is a practical exercise in backend engineering, covering REST API design, authentication, database relationships, schema validation, migrations, and automated testing.

It also addresses a real personal use case: organizing music and tracking practice sessions in one place.

---

**Repository:** [music-practice-api](https://github.com/DanielPixleyPulukuri/music-practice-api)