"""FastAPI routes for SMTP configuration and testing."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.smtp.models.schemas import (
    ConfigStatusResponse,
    ConnectionTestRequest,
    SendTestEmailRequest,
    SMTPCredentials,
    StatusResponse,
)
from app.smtp.services.smtp_service import smtp_service

router = APIRouter(prefix="/smtp", tags=["SMTP"])


@router.get(
    "/status",
    response_model=ConfigStatusResponse,
    summary="Check whether SMTP credentials are configured",
)
def get_status() -> ConfigStatusResponse:
    creds = smtp_service.get_credentials()
    if creds is None:
        return ConfigStatusResponse(
            configured=False,
            host="",
            port=0,
            username="",
            use_tls=True,
            use_ssl=False,
            from_email="",
            from_name="",
            password_set=False,
        )
    return ConfigStatusResponse(
        configured=True,
        host=creds.host,
        port=creds.port,
        username=creds.username,
        use_tls=creds.use_tls,
        use_ssl=creds.use_ssl,
        from_email=str(creds.from_email or ""),
        from_name=creds.from_name,
        password_set=bool(creds.password),
    )


@router.post(
    "/credentials",
    response_model=StatusResponse,
    summary="Save SMTP credentials in memory",
)
def save_credentials(credentials: SMTPCredentials) -> StatusResponse:
    saved = smtp_service.save_credentials(credentials)
    return StatusResponse(
        success=True,
        message="SMTP credentials saved. They stay in memory until the server restarts.",
        details={
            "host": saved.host,
            "port": saved.port,
            "username": saved.username,
            "from_email": str(saved.from_email),
            "use_tls": saved.use_tls,
            "use_ssl": saved.use_ssl,
        },
    )


@router.delete(
    "/credentials",
    response_model=StatusResponse,
    summary="Clear saved SMTP credentials",
)
def clear_credentials() -> StatusResponse:
    smtp_service.clear_credentials()
    return StatusResponse(success=True, message="Saved SMTP credentials cleared.")


@router.post(
    "/test-connection",
    response_model=StatusResponse,
    summary="Login to the SMTP server without sending mail",
)
def test_connection(payload: Optional[ConnectionTestRequest] = None) -> StatusResponse:
    payload = payload or ConnectionTestRequest()
    try:
        details = smtp_service.test_connection(payload.credentials)
        return StatusResponse(
            success=True,
            message="SMTP connection successful. Your credentials work.",
            details=details,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"SMTP connection failed: {exc}",
        ) from exc


@router.post(
    "/send-test",
    response_model=StatusResponse,
    summary="Send a test email to verify end-to-end delivery",
)
def send_test_email(payload: SendTestEmailRequest) -> StatusResponse:
    try:
        details = smtp_service.send_test_email(
            to_email=str(payload.to_email),
            subject=payload.subject,
            body=payload.body,
            override=payload.credentials,
        )
        return StatusResponse(
            success=True,
            message="Test email sent successfully. Check the inbox (and spam folder).",
            details=details,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send test email: {exc}",
        ) from exc
