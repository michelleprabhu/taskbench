# jira_client.py
import json
import base64
import requests
from typing import Dict, Any, List, Optional
from config import get_settings

S = get_settings()


def _auth_headers() -> Dict[str, str]:
    if not (S.JIRA_BASE and S.JIRA_EMAIL and S.JIRA_API_TOKEN):
        raise RuntimeError("Set JIRA_BASE, JIRA_EMAIL, JIRA_API_TOKEN in .env")
    token = f"{S.JIRA_EMAIL}:{S.JIRA_API_TOKEN}"
    b64 = base64.b64encode(token.encode()).decode()
    return {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# --------------------------- Jira helpers ---------------------------

def list_fields() -> List[Dict[str, Any]]:
    url = f"{S.JIRA_BASE}/rest/api/3/field"
    r = requests.get(url, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def list_project_issue_types(project_key: str) -> List[str]:
    url = f"{S.JIRA_BASE}/rest/api/3/issue/createmeta?projectKeys={project_key}"
    r = requests.get(url, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    names: List[str] = []
    for proj in data.get("projects", []):
        for it in proj.get("issuetypes", []):
            n = it.get("name")
            if n:
                names.append(n)
    # unique while preserving order
    seen, out = set(), []
    for n in names:
        if n not in seen:
            out.append(n); seen.add(n)
    return out


def search_user_by_email(email: str) -> List[Dict[str, Any]]:
    url = f"{S.JIRA_BASE}/rest/api/3/user/search?query={email}"
    r = requests.get(url, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


# --------------------------- ADF helpers ---------------------------

def _adf_text_paragraph(text: str) -> Dict[str, Any]:
    text = (text or "").rstrip()
    if not text:
        # blank paragraph
        return {"type": "paragraph"}
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _adf_heading(text: str, level: int = 3) -> Dict[str, Any]:
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": text}],
    }


def _adf_bullet_list(items: List[str]) -> Dict[str, Any]:
    list_items = []
    for it in items:
        list_items.append({
            "type": "listItem",
            "content": [_adf_text_paragraph(it)]
        })
    return {"type": "bulletList", "content": list_items}


def _to_adf(description: str, acceptance: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Minimal, robust ADF that Jira Cloud accepts.
    - Turns each line of `description` into a paragraph (blank lines -> empty paragraph)
    - Appends an "Acceptance Criteria" heading + bullet list if provided
    """
    content: List[Dict[str, Any]] = []

    # split into lines; make paragraphs
    lines = (description or "").splitlines()
    if not lines:
        content.append(_adf_text_paragraph(" "))  # Jira dislikes completely empty docs
    else:
        for ln in lines:
            content.append(_adf_text_paragraph(ln))

    # append AC if present
    if acceptance:
        content.append(_adf_heading("Acceptance Criteria", level=3))
        content.append(_adf_bullet_list(acceptance))

    return {"type": "doc", "version": 1, "content": content}


def _is_bad(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() == S.IGNORE_PLACEHOLDER_LITERAL.lower()


# --------------------------- payload + create ---------------------------

def _payload_for_story(story: Dict[str, Any], customfields: Dict[str, str]) -> Dict[str, Any]:
    issuetype_name = (story.get("issuetype_name") or S.DEFAULT_ISSUETYPE or "Story").strip()

    fields: Dict[str, Any] = {
        "project": {"key": story["project_key"]},
        "summary": story["summary"],
        # 👇 ADF description
        "description": _to_adf(story.get("description", ""), story.get("acceptance_criteria")),
        "issuetype": {"name": issuetype_name},
        "labels": story.get("labels", []),
    }

    # Priority / Components are off by default for Team-managed projects
    if getattr(S, "SEND_PRIORITY", False) and story.get("priority"):
        fields["priority"] = {"name": story["priority"]}

    if getattr(S, "SEND_COMPONENTS", False) and story.get("components"):
        comps = [{"name": c} for c in story["components"] if not _is_bad(c)]
        if comps:
            fields["components"] = comps

    if story.get("assignee_account_id"):
        fields["assignee"] = {"accountId": story["assignee_account_id"]}

    # Optional custom fields (site-specific)
    sp_cf = (customfields.get("story_points") or "").strip()
    if not _is_bad(sp_cf) and story.get("story_points") is not None:
        fields[sp_cf] = story["story_points"]

    epic_link_cf = (customfields.get("epic_link") or "").strip()
    if not _is_bad(epic_link_cf) and story.get("epic_link"):
        fields[epic_link_cf] = story["epic_link"]

    # Epic Name (for later when you create Epics)
    epic_name_cf = (customfields.get("epic_name") or "").strip()
    if issuetype_name.lower() == "epic" and not _is_bad(epic_name_cf):
        fields[epic_name_cf] = story.get("epic_name") or story["summary"]

    return {"fields": fields}


def create_issue(story: Dict[str, Any], customfields: Dict[str, str]) -> Dict[str, Any]:
    url = f"{S.JIRA_BASE}/rest/api/3/issue"
    payload = _payload_for_story(story, customfields)
    r = requests.post(url, headers=_auth_headers(), data=json.dumps(payload), timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Jira create failed: {r.status_code} {r.text}")
    return r.json()
