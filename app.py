# app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

from models import (
    ConvertResult, JiraCreateResponse,
    BulkConvertRequest, BulkConvertResult,
    JiraField, Health, JiraStory
)
from config import get_settings
from parsers import extract_text, parse_text, decode_base64
import jira_client


S = get_settings()
app = FastAPI(
    title=S.API_TITLE,
    version=S.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------  ------------
def _clean_csv(s: Optional[str]) -> List[str]:
    toks = []
    for x in (s or "").split(","):
        v = x.strip()
        if v and v.lower() != S.IGNORE_PLACEHOLDER_LITERAL.lower():
            toks.append(v)
    return toks

def _clean_cf_id(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    v = s.strip()
    if v == "" or v.lower() == S.IGNORE_PLACEHOLDER_LITERAL.lower():
        return None
    return v

# ---------------- Health  ----------------
@app.get("/health", response_model=Health)
def health():
    return Health(status="ok")

# ---------------- Jira helpers ----------------
@app.get("/jira/fields", response_model=List[JiraField])
def jira_fields():
    try:
        data = jira_client.list_fields()
        return [JiraField(id=f["id"], name=f["name"], schema_info=f.get("schema", {})) for f in data]
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/jira/issue-types")
def jira_issue_types(project_key: str):
    try:
        return {"project_key": project_key, "issuetypes": jira_client.list_project_issue_types(project_key)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ---------------- Convert ----------------
@app.post("/convert", response_model=ConvertResult)
async def convert(
    file: UploadFile = File(...),
    project_key: str = Form(...),
    default_labels: Optional[str] = Form(None),
    default_components: Optional[str] = Form(None),
):
    b = await file.read()
    raw = extract_text(
        file.filename, b,
        enable_html=S.ENABLE_HTML, max_pages=S.MAX_PAGES,
        enable_ocr=S.ENABLE_OCR, ocr_lang=S.OCR_LANG,
    )
    labels = _clean_csv(default_labels)
    comps  = _clean_csv(default_components)

    story_dict, diag = parse_text(
        raw, project_key, labels, comps,
        options={"priority_map": {}, "max_chars": S.MAX_TEXT_CHARS},
    )
    return ConvertResult(story=JiraStory(**story_dict), raw_text=raw, diagnostics=diag)

# ---------------- Convert + Create in Jira ----------------
@app.post("/jira/create", response_model=JiraCreateResponse)
async def jira_create(
    file: UploadFile = File(...),
    project_key: str = Form(...),
    default_labels: Optional[str] = Form(None),
    default_components: Optional[str] = Form(None),
    story_points_cf: Optional[str] = Form(None),   # e.g. customfield_10016
    epic_link_cf: Optional[str] = Form(None),      # e.g. customfield_10014
    issuetype_name: str = Form(get_settings().DEFAULT_ISSUETYPE),
    epic_name_cf: Optional[str] = Form(None),      # only for Epic 
):
    b = await file.read()
    raw = extract_text(
        file.filename, b,
        enable_html=S.ENABLE_HTML, max_pages=S.MAX_PAGES,
        enable_ocr=S.ENABLE_OCR, ocr_lang=S.OCR_LANG,
    )
    labels = _clean_csv(default_labels)
    comps  = _clean_csv(default_components)

    story_dict, _ = parse_text(
        raw, project_key, labels, comps,
        options={"priority_map": {}, "max_chars": S.MAX_TEXT_CHARS},
    )
    story_dict["issuetype_name"] = issuetype_name

    try:
        created = jira_client.create_issue(
            story_dict,
            customfields={
                "story_points": _clean_cf_id(story_points_cf) or "",
                "epic_link":   _clean_cf_id(epic_link_cf) or "",
                "epic_name":   _clean_cf_id(epic_name_cf) or "",
            },
        )
        return JiraCreateResponse(key=created["key"], self_url=created["self"], story=JiraStory(**story_dict))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Bulk convert  ----------------
@app.post("/bulk/convert", response_model=BulkConvertResult)
def bulk_convert(payload: BulkConvertRequest):
    items = []
    for i, name in enumerate(payload.filenames):
        if payload.mode == "base64":
            b = decode_base64(payload.files[i])
        else:
            with open(payload.files[i], "rb") as fh:
                b = fh.read()

        raw = extract_text(
            name, b,
            enable_html=S.ENABLE_HTML, max_pages=S.MAX_PAGES,
            enable_ocr=S.ENABLE_OCR, ocr_lang=S.OCR_LANG,
        )
        story_dict, diag = parse_text(
            raw, payload.project_key, [], [],
            options={"priority_map": {}, "max_chars": S.MAX_TEXT_CHARS},
        )
        items.append(ConvertResult(story=JiraStory(**story_dict), raw_text=raw, diagnostics=diag))
    return BulkConvertResult(items=items)
