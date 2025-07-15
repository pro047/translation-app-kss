from pydantic import BaseModel
from typing import List


class TextRequest(BaseModel):
    id: str
    text: str


class SentenceResponse(BaseModel):
    sentences: List[str]
