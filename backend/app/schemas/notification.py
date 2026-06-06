from datetime import datetime

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str | None = None
    type: NotificationType
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
