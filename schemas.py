from pydantic import BaseModel
from typing import List


class ResearchReport(BaseModel):
    topic: str
    introduction: str
    key_findings: List[str]
    conclusion: str
    sources: List[str]
