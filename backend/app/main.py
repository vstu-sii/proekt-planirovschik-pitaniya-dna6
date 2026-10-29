import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.plans import router as plans_router
from app.core.config import settings

app = FastAPI(title="Meal Planner API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plans_router)


def error_response(status_code: int, message: str, details: object | None = None) -> JSONResponse:
    error_names = {
        400: "invalid_json",
        404: "not_found",
        422: "validation_error",
        429: "rate_limited",
        502: "provider_error",
        503: "service_unavailable",
        504: "timeout",
    }
    request_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=status_code,
        headers={"X-Request-ID": request_id},
        content={
            "error": error_names.get(status_code, "internal_error"),
            "message": message,
            "request_id": request_id,
            "details": jsonable_encoder(details) if details is not None else {},
        },
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "Request validation failed", exc.errors())


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Meal Planner API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
