"""SMTP connection and email-sending service."""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from app.core.config import Settings, get_settings
from app.smtp.models.schemas import SMTPCredentials


class SMTPService:
    """Holds runtime credentials and talks to an SMTP server."""

    def __init__(self) -> None:
        self._credentials: Optional[SMTPCredentials] = None

    def load_from_settings(self, settings: Optional[Settings] = None) -> None:
        settings = settings or get_settings()
        if not settings.smtp_username or not settings.smtp_password:
            return
        self._credentials = SMTPCredentials(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
            use_ssl=settings.smtp_use_ssl,
            from_email=settings.smtp_from_email or settings.smtp_username,
            from_name=settings.smtp_from_name,
        )

    def save_credentials(self, credentials: SMTPCredentials) -> SMTPCredentials:
        if not credentials.from_email:
            credentials = credentials.model_copy(
                update={"from_email": credentials.username}
            )
        self._credentials = credentials
        return credentials

    def get_credentials(self) -> Optional[SMTPCredentials]:
        return self._credentials

    def clear_credentials(self) -> None:
        self._credentials = None

    def resolve(
        self, override: Optional[SMTPCredentials] = None
    ) -> SMTPCredentials:
        if override is not None:
            if not override.from_email:
                return override.model_copy(update={"from_email": override.username})
            return override
        if self._credentials is None:
            raise ValueError(
                "No SMTP credentials configured. "
                "POST /smtp/credentials or set values in .env first."
            )
        return self._credentials

    def test_connection(
        self, override: Optional[SMTPCredentials] = None
    ) -> dict:
        creds = self.resolve(override)
        with self._open_client(creds) as client:
            code, message = client.noop()
        return {
            "host": creds.host,
            "port": creds.port,
            "username": creds.username,
            "use_tls": creds.use_tls,
            "use_ssl": creds.use_ssl,
            "smtp_code": code,
            "smtp_message": message.decode(errors="replace")
            if isinstance(message, bytes)
            else str(message),
        }

    def send_test_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        override: Optional[SMTPCredentials] = None,
    ) -> dict:
        creds = self.resolve(override)
        from_email = str(creds.from_email or creds.username)

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{creds.from_name} <{from_email}>"
        message["To"] = to_email
        message.set_content(body)

        with self._open_client(creds) as client:
            client.send_message(message)

        return {
            "to": to_email,
            "from": from_email,
            "subject": subject,
            "host": creds.host,
            "port": creds.port,
        }

    def _open_client(self, creds: SMTPCredentials):
        if creds.use_ssl and creds.use_tls:
            raise ValueError(
                "Choose either use_ssl (port 465) or use_tls (port 587), not both."
            )

        context = ssl.create_default_context()
        timeout = 20

        if creds.use_ssl:
            client = smtplib.SMTP_SSL(
                creds.host, creds.port, timeout=timeout, context=context
            )
        else:
            client = smtplib.SMTP(creds.host, creds.port, timeout=timeout)
            client.ehlo()
            if creds.use_tls:
                client.starttls(context=context)
                client.ehlo()

        client.login(creds.username, creds.password)
        return client


smtp_service = SMTPService()
