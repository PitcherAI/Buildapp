from pydantic import BaseModel
from typing import List, Optional

class Attachment(BaseModel):
    name: str
    url: str

class TaskRequest(BaseModel):
    task: str
    email: str
    round: int = 1
    brief: str
    evaluation_url: str
    nonce: str
    secret: str
    attachments: List[Attachment] = []