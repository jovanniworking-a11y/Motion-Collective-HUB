"""Muse data platform — SQLAlchemy models (SQLite now, Postgres via DATABASE_URL).

Privacy MVP: store counts/features/hashes only — never faces, guest names, or venue address.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import Float, Integer, String, Text, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import DATA_DIR, database_url_from_env

DATABASE_URL = database_url_from_env() or f"sqlite:///{(DATA_DIR / 'muse_platform.sqlite3').as_posix()}"


class Base(DeclarativeBase):
    pass


class SimRun(Base):
    __tablename__ = "sim_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False, default=time.time)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, default="smoke-stub")
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    params_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    result_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    label: Mapped[str] = mapped_column(String(32), nullable=False, default="estimate")
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="muse")


class ImagingObservation(Base):
    __tablename__ = "imaging_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False, default=time.time)
    captured_at: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Density / crew-count placeholders only — no face embeddings.
    crew_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    density_est: Mapped[float | None] = mapped_column(Float, nullable=True)
    zone: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    image_path_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    label: Mapped[str] = mapped_column(String(32), nullable=False, default="estimate")
    note: Mapped[str] = mapped_column(String(256), nullable=False, default="no faces/PII stored")


class DrinkEvent(Base):
    __tablename__ = "drink_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False, default=time.time)
    station: Mapped[str] = mapped_column(String(64), nullable=False, default="island")
    drink_type: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="sim")
    label: Mapped[str] = mapped_column(String(32), nullable=False, default="estimate")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OccupancySample(Base):
    """One zone count. No image, boxes, track ids, or names."""

    __tablename__ = "occupancy_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    captured_at: Mapped[float] = mapped_column(Float, nullable=False)
    zone: Mapped[str] = mapped_column(String(32), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    count_quality: Mapped[str] = mapped_column(String(16), nullable=False)
    camera_id: Mapped[str] = mapped_column(String(32), nullable=False)
    sample_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    label: Mapped[str] = mapped_column(String(16), nullable=False, default="estimate")


class FlowCount(Base):
    __tablename__ = "flow_counts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False, default=time.time)
    zone: Mapped[str] = mapped_column(String(64), nullable=False, default="dance")
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    window_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="sim")
    label: Mapped[str] = mapped_column(String(32), nullable=False, default="estimate")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


_engine = None
_SessionLocal = None


def _make_engine():
    connect_args: dict[str, Any] = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    eng = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
    if DATABASE_URL.startswith("sqlite"):

        @event.listens_for(eng, "connect")
        def _sqlite_pragma(dbapi_conn, _connection_record):  # type: ignore[no-untyped-def]
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return eng


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = _make_engine()
        _SessionLocal = sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            future=True,
            expire_on_commit=False,
        )
    return _engine


def get_session_factory():
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def init_platform_db() -> dict[str, Any]:
    eng = get_engine()
    Base.metadata.create_all(eng)
    return {
        "ok": True,
        "database_url_scheme": DATABASE_URL.split(":", 1)[0],
        "sqlite": DATABASE_URL.startswith("sqlite"),
        "tables": sorted(Base.metadata.tables.keys()),
        "label": "confirmed",
    }


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
