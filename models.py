# models.py
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class JiraStory(BaseModel):
    project_key: str = Field(..., description="Jira project key (e.g., TD)")
    summary: str
    description: str
    acceptance_criteria: List[str] = []
    labels: List[str] = []
    components: List[str] = []
    story_points: Optional[float] = None
    priority: Optional[str] = None
    epic_link: Optional[str] = None
    assignee_account_id: Optional[str] = None
    issuetype_name: Optional[str] = None
    epic_name: Optional[str] = None


class ConvertResult(BaseModel):
    story: JiraStory
    raw_text: str
    diagnostics: Dict[str, Any] = {}


class JiraCreateResponse(BaseModel):
    key: str
    self_url: str
    story: JiraStory


class JiraField(BaseModel):
    id: str
    name: str
    schema_info: Dict[str, Any] = {}


class Health(BaseModel):
    status: str = "ok"


class BulkConvertRequest(BaseModel):
    mode: Literal["base64", "path"] = "base64"
    filenames: List[str]
    files: List[str]
    project_key: str


class BulkConvertResult(BaseModel):
    items: List[ConvertResult]
