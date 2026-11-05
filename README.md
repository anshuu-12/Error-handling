# FastAPI Pydantic v2 Validation & Error Handling

A containerized RESTful API built with **FastAPI**[cite: 1], **Pydantic v2**, **Pytest**, and **Docker**[cite: 1] demonstrating strict request/response schema validation, custom field constraints, unified error handling, and automated testing for the Users master module[cite: 1].

---

## Architecture & Validation Flow

```text
HTTP Request (Client / Postman)
       │
       ▼
 1. Uvicorn (ASGI Server)
       │
       ▼
 2. FastAPI Application (app/main.py)
       │
       ├──► 3. Pydantic v2 Schema Validation (app/schemas/user.py)
       │         │
       │         └── [Invalid Input] ──► RequestValidationError Handler ──► 422 JSON Error
       │
       ▼
 4. APIRouter (app/routers/users.py)
       │
       ├──► [Duplicate Email / Empty Body] ──► HTTPException Handler ──► 400 JSON Error
       ├──► [User ID Not Found]            ──► HTTPException Handler ──► 404 JSON Error
       │
       ▼
 5. In-Memory Data Store (fake_users_db)
       │
       ▼
 6. Response Serialization (UserResponse) ──► 200 OK / 201 Created
```

### Directory Structure

```text
FastAPI-Validation/
├── .vscode/
│   └── settings.json
├── app/
│   ├── __init__.py
│   ├── main.py              # App entry point & global exception handlers
│   ├── models/              # Domain data models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/             # CRUD endpoints & HTTPExceptions (400, 404)
│   │   ├── __init__.py
│   │   └── users.py
│   └── schemas/             # Pydantic v2 schemas, Field constraints & validators
│       ├── __init__.py
│       └── user.py
├── tests/
│   ├── __init__.py
│   └── test_users.py        # Automated pytest suite for validation & error cases
├── postman/
│   └── users_validation_collection.json
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Core Concepts Explained

### 1. What is Pydantic & What is a Schema?
- **Schema:** A data contract that defines the expected fields, data types, default values, and validation rules for API requests and responses.
- **Pydantic v2:** A data validation and serialization library powered by a Rust core (`pydantic-core`). It uses Python type hints, `Field()` constraints, and `@field_validator` decorators to validate incoming payloads and return clear, structured error messages when data is invalid.

### 2. How FastAPI Uses Pydantic
- **Request Validation:** FastAPI automatically parses incoming JSON bodies against the route's Pydantic schema (`UserCreate`, `UserUpdate`)[cite: 1]. If fields are missing, have the wrong type, or violate constraints, FastAPI halts execution before the endpoint runs and raises a `422 Unprocessable Entity` error[cite: 1].
- **Response Serialization:** Using `response_model=UserResponse`[cite: 1] ensures outgoing data conforms to the response contract and strips any unintended fields.

### 3. Status Codes & Error Handling
| Status Code | Meaning | When Our API Returns It |
| :--- | :--- | :--- |
| **`200 OK`** | Standard Success | `GET` (fetch users), `PUT` (update user), or `DELETE` (remove user) succeeds[cite: 1]. |
| **`201 Created`** | Resource Created | `POST /users/` successfully creates a new user record[cite: 1]. |
| **`400 Bad Request`** | Business Logic Error | Client attempts to register a duplicate email address or sends an empty `PUT` payload. |
| **`404 Not Found`** | Resource Missing | Client requests, updates, or deletes a `user_id` that does not exist[cite: 1]. |
| **`422 Unprocessable Entity`** | Validation Error | Request payload has missing required fields, wrong data types, or out-of-range values[cite: 1]. |

---

## Pydantic v2 Schema Rules (`app/schemas/user.py`)

| Field | Type | Required / Default | Constraints & Validation Rules |
| :--- | :--- | :--- | :--- |
| `name` | `str` | **Required** (`...`) | `min_length=2`, `max_length=50`, trimmed whitespace, cannot contain numbers. |
| `email` | `EmailStr` | **Required** (`...`) | Must be a valid email format (`user@domain.com`). |
| `phone` | `str` | **Required** (`...`) | Custom regex validator: must be exactly 10 digits (`0-9`). |
| `age` | `int` | **Required** (`...`) | `ge=18` (greater than or equal to 18) and `le=100` (less than or equal to 100). |
| `status` | `Literal["active", "inactive"]` | **Default:** `"active"` | Must be either `"active"` or `"inactive"`. |

- **Strict Payload Checking:** `model_config = ConfigDict(extra="forbid")` rejects unexpected fields not defined in the schema.
- **ORM Compatibility:** `model_config = ConfigDict(from_attributes=True)` on `UserResponse`.

---

## Consistent Error Response Format

All API errors (`400`, `404`, and `422`) are intercepted by custom exception handlers in `app/main.py` to return a single, predictable JSON structure:

### Example 1: Validation Error (`422 Unprocessable Entity`)
```json
{
  "status": "error",
  "status_code": 422,
  "message": "Validation failed for the provided input data",
  "errors": [
    {
      "field": "age",
      "message": "Input should be greater than or equal to 18",
      "type": "greater_than_equal"
    }
  ]
}
```

### Example 2: Resource Not Found (`404 Not Found`)
```json
{
  "status": "error",
  "status_code": 404,
  "message": "User with ID 999 not found",
  "errors": null
}
```

---

## How to Run the Application

### 1. Run with Docker Compose (Recommended)
1. Build and start the container in detached mode[cite: 1]:
   ```bash
   docker compose up --build -d
   ```
2. Check container status[cite: 1]:
   ```bash
   docker compose ps
   ```
3. Stop the container[cite: 1]:
   ```bash
   docker compose down
   ```

### 2. Run Automated Tests (`pytest`)
Execute the test suite inside the running Docker container:
```bash
docker compose exec web pytest -v
```
Or locally with a virtual environment:
```bash
pytest -v
```

### 3. Access Interactive API Docs
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)[cite: 1]
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)[cite: 1]

---

## Postman Testing Guide

Import `postman/users_validation_collection.json` into Postman[cite: 1] and test the following scenarios:

| # | Scenario | Method & Endpoint | Request Body (JSON) | Expected Status |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Valid User Creation (Default `status`)** | `POST /users/` | `{"name": "Ansh Rohit", "email": "ansh@example.com", "phone": "9876543210", "age": 22}` | `201 Created` |
| **2** | **Missing Required Fields** | `POST /users/` | `{"name": "Ansh Rohit"}` | `422 Unprocessable Entity` |
| **3** | **Wrong Data Types** | `POST /users/` | `{"name": "Ansh Rohit", "email": "not-an-email", "phone": "9876543210", "age": "twenty"}` | `422 Unprocessable Entity` |
| **4** | **Out-of-Range Values** | `POST /users/` | `{"name": "A", "email": "ansh@example.com", "phone": "123", "age": 12}` | `422 Unprocessable Entity` |
| **5** | **User Does Not Exist** | `GET /users/999` | *None* | `404 Not Found` |
| **6** | **Duplicate Email Check** | `POST /users/` | *(Send Case 1 payload a second time)* | `400 Bad Request` |