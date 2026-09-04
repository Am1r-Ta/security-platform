from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    agent_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True
    )

    hostname: Mapped[str] = mapped_column(String(255))
    os: Mapped[str] = mapped_column(String(100))
    os_version: Mapped[str] = mapped_column(String(100))
    architecture: Mapped[str] = mapped_column(String(100))
    python_version: Mapped[str] = mapped_column(String(50))

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    agent_id: Mapped[str] = mapped_column(
        String(36),
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(100)
    )

    pid: Mapped[int | None] = mapped_column(
        nullable=True
    )

    process_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    severity: Mapped[str] = mapped_column(
        String(20)
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    event_id: Mapped[int] = mapped_column(
        index=True
    )

    agent_id: Mapped[str] = mapped_column(
        String(36),
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    severity: Mapped[str] = mapped_column(
        String(20)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="open"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )