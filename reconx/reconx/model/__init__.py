from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class Evidence(BaseModel):
    type: str
    port: Optional[int] = None
    proto: Optional[str] = None
    service: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None

class Finding(BaseModel):
    id: str
    title: str
    severity: str = "info"
    evidence_ref: str | None = None

class Artifact(BaseModel):
    kind: str
    path: str

class SummaryModel(BaseModel):
    layer: int
    target: str
    evidence: List[Evidence] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    artifacts: List[Artifact] = Field(default_factory=list)

class Action(BaseModel):
    tool: str
    args: dict
    target: str
    priority: int = 5

class Result(BaseModel):
    summary: SummaryModel
    artifacts: list[str] = Field(default_factory=list)
    logs: str | None = None
