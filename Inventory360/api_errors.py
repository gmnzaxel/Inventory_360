import logging
from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _request_id_from(request) -> Optional[str]:
    if request is None:
        return None
    return getattr(request, 'request_id', None) or request.headers.get('X-Request-ID')


def build_error_payload(
    *,
    title: str,
    message: str,
    code: str,
    request=None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "error": {
            "title": title,
            "message": message,
            "code": code,
        }
    }
    if details:
        payload["error"]["details"] = details
    request_id = _request_id_from(request)
    if request_id:
        payload["error"]["requestId"] = request_id
    return payload


class ApiError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "error.bad_request"
    default_detail = "La solicitud contiene datos invalidos."
    default_title = "Solicitud invalida"

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        title: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        request=None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if status_code is not None:
            self.status_code = status_code
        message = detail or self.default_detail
        payload = build_error_payload(
            title=title or self.default_title,
            message=message,
            code=code or self.default_code,
            request=request,
            details=details,
        )["error"]
        super().__init__(payload)


class ConflictError(ApiError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "error.conflict"
    default_detail = "El recurso ya existe."
    default_title = "Conflicto de datos"


class ForbiddenError(ApiError):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "error.forbidden"
    default_detail = "No tienes permisos para realizar esta accion."
    default_title = "Acceso denegado"


def _flatten_validation_errors(data: Any) -> Dict[str, str]:
    if isinstance(data, dict):
        flattened: Dict[str, str] = {}
        for key, value in data.items():
            msg = _stringify(value)
            flattened[key] = msg
        return flattened
    if isinstance(data, list):
        joined = " ".join(_stringify(item) for item in data)
        return {"non_field_errors": joined}
    return {"detail": _stringify(data)}


def _stringify(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return " ".join(_stringify(v) for v in value)
    return str(value)


def inventory_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    request = context.get("request")

    if response is None:
        logger.exception("Unhandled exception", exc_info=exc)
        payload = build_error_payload(
            title="Error inesperado",
            message="Ocurrio un error interno. Intentalo nuevamente o contacta al soporte.",
            code="error.internal",
            request=request,
        )
        return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, ApiError):
        payload = {"error": response.data}
        response.data = payload
        return response

    if isinstance(exc, ValidationError):
        flattened = _flatten_validation_errors(response.data)
        message = flattened.get("non_field_errors") or flattened.get("detail")
        if not message:
            message = " ".join(f"{k}: {v}" for k, v in flattened.items())
        payload = build_error_payload(
            title="Solicitud invalida",
            message=message or "La solicitud contiene errores.",
            code="error.validation",
            request=request,
            details=flattened,
        )
        response.data = payload
        return response

    if response.status_code >= 500:
        logger.exception("Server error", exc_info=exc)

    if isinstance(response.data, dict):
        message = _stringify(response.data.pop("detail", "")) or "Ocurrio un error."
        details = _flatten_validation_errors(response.data) if response.data else None
        payload = build_error_payload(
            title="Error",
            message=message,
            code=f"error.http.{response.status_code}",
            request=request,
            details=details,
        )
    else:
        payload = build_error_payload(
            title="Error",
            message=_stringify(response.data),
            code=f"error.http.{response.status_code}",
            request=request,
        )

    response.data = payload
    return response
