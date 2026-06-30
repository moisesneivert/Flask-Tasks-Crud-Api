"""JSON API exceptions and error handlers."""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base exception for expected API errors."""

    status_code = 400
    code = "api_error"
    default_message = "The request could not be processed."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message
        self.details = details


class ValidationError(ApiError):
    """Raised when request data is invalid."""

    status_code = 400
    code = "validation_error"
    default_message = "The request data is invalid."


class UnsupportedMediaTypeError(ApiError):
    """Raised when the request does not contain JSON."""

    status_code = 415
    code = "unsupported_media_type"
    default_message = "Content-Type must be application/json."


class NotFoundError(ApiError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    code = "not_found"
    default_message = "The requested resource was not found."


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
):
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        body["error"]["details"] = details
    return jsonify(body), status_code


def register_error_handlers(app: Flask) -> None:
    """Register JSON error handlers for expected and unexpected errors."""

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return _error_response(
            status_code=error.status_code,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        code = error.name.lower().replace(" ", "_")
        return _error_response(
            status_code=error.code or 500,
            code=code,
            message=error.description,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Unexpected application error", exc_info=error)
        return _error_response(
            status_code=500,
            code="internal_server_error",
            message="An unexpected error occurred.",
        )
