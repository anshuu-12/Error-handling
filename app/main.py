from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import users

app = FastAPI(
    title="User Management API - Pydantic v2 & Error Handling",
    description="Users master CRUD with Pydantic v2 validation constraints and consistent error responses",
    version="2.0.0"
)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "status_code": exc.status_code,
            "message": exc.detail,
            "errors": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        formatted_errors.append({
            "field": field_path or "body",
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "status_code": 422,
            "message": "Validation failed for the provided input data",
            "errors": formatted_errors
        }
    )

app.include_router(users.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}