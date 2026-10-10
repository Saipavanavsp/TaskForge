import uuid
from datetime import datetime, timezone
from sqlalchemy import String, TypeDecorator, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type.
    Uses PostgreSQL's native UUID type, otherwise uses CHAR(36) storing as string.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value) if isinstance(value, uuid.UUID) else value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class Base(DeclarativeBase):
    pass
