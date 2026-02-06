import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class DocumentMetadata(Base):
    __tablename__ = "documents_metadata"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )

    # Identidade do documento
    doc_id = Column(String, unique=True, index=True, nullable=False)

    # Metadados do PDF
    producer = Column(String, nullable=True)
    creator = Column(String, nullable=True)

    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    keywords = Column(String, nullable=True)

    format = Column(String, nullable=True)
    trapped = Column(String, nullable=True)

    # Datas (normalizadas)
    creation_date = Column(DateTime(timezone=True), nullable=True)
    modification_date = Column(DateTime(timezone=True), nullable=True)

    # Datas raw do PDF (útil para debug/auditoria)
    creation_date_raw = Column(String, nullable=True)
    modification_date_raw = Column(String, nullable=True)

    # Arquivo
    source = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    total_pages = Column(Integer, nullable=False)

    # Controle
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
