"""SMTP request and response schemas."""

from app.smtp.models.schemas import (
    ConfigStatusResponse,
    ConnectionTestRequest,
    SendTestEmailRequest,
    SMTPCredentials,
    StatusResponse,
)

__all__ = [
    "ConfigStatusResponse",
    "ConnectionTestRequest",
    "SendTestEmailRequest",
    "SMTPCredentials",
    "StatusResponse",
]
