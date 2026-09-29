"""Request and response models for the SMTP module."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SMTPCredentials(BaseModel):
    """SMTP server login details."""

    host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server hostname",
        examples=["smtp.gmail.com"],
    )
    port: int = Field(
        default=587,
        description="SMTP port (587 for TLS, 465 for SSL)",
        examples=[587],
    )
    username: str = Field(
        ...,
        description="SMTP username (usually your full email)",
        examples=["you@gmail.com"],
    )
    password: str = Field(
        ...,
        description="SMTP password or Gmail App Password",
        examples=["xxxx xxxx xxxx xxxx"],
    )
    use_tls: bool = Field(
        default=True,
        description="Use STARTTLS (typical for port 587)",
    )
    use_ssl: bool = Field(
        default=False,
        description="Use SSL from the start (typical for port 465)",
    )
    from_email: Optional[EmailStr] = Field(
        default=None,
        description="From address (defaults to username if omitted)",
    )
    from_name: str = Field(
        default="SMTP Test Server",
        description="Display name for the sender",
    )


class ConnectionTestRequest(BaseModel):
    """Optional credentials for a one-off connection test."""

    credentials: Optional[SMTPCredentials] = Field(
        default=None,
        description="If omitted, saved/default credentials are used",
    )


class SendTestEmailRequest(BaseModel):
    """Payload for sending a test email."""

    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(
        default="SMTP Test Email",
        description="Email subject line",
    )
    body: str = Field(
        default="Hello! If you received this, your SMTP setup is working.",
        description="Plain-text email body",
    )
    credentials: Optional[SMTPCredentials] = Field(
        default=None,
        description="If omitted, saved/default credentials are used",
    )


class StatusResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None


class ConfigStatusResponse(BaseModel):
    configured: bool
    host: str
    port: int
    username: str
    use_tls: bool
    use_ssl: bool
    from_email: str
    from_name: str
    password_set: bool
