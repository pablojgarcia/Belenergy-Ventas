import uuid
from sqlalchemy.orm import Session
from .. import models


class DraftLineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_draft_id(self, draft_id: uuid.UUID) -> list[models.QuotationDraftLine]:
        return self.db.query(models.QuotationDraftLine).filter(
            models.QuotationDraftLine.draft_id == draft_id
        ).order_by(models.QuotationDraftLine.created_at).all()

    def create(self, line: models.QuotationDraftLine) -> models.QuotationDraftLine:
        self.db.add(line)
        self.db.flush()
        return line

    def delete_by_draft_id(self, draft_id: uuid.UUID):
        self.db.query(models.QuotationDraftLine).filter(
            models.QuotationDraftLine.draft_id == draft_id
        ).delete()
