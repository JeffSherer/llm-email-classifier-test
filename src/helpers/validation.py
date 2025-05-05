import logging
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class EmailInput(BaseModel):
    id: str
    subject: str
    body: str
    from_: Optional[EmailStr] = "unknown@example.com"

async def validate_email_data(email_data: Dict) -> Optional[EmailInput]:
    try:
        return EmailInput(**email_data)
    except ValidationError as e:
        logger.error(f"Validation failed for incoming email data: {e}\nInvalid data: {email_data}")
        return None
