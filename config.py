# config.py
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Shown on /docs
    API_TITLE: str = "Taskbench — Doc→Jira"
    API_VERSION: str = "1.5.0"

    # Jira credentials
    JIRA_BASE: str | None = None           
    JIRA_EMAIL: str | None = None
    JIRA_API_TOKEN: str | None = None

    # Default
    DEFAULT_ISSUETYPE: str = "Story"

    # Parsing / OCR
    ENABLE_HTML: bool = False
    ENABLE_OCR: bool = True
    OCR_LANG: str = "eng"
    MAX_PAGES: int = 50
    MAX_TEXT_CHARS: int = 400000

    # Team-managed 
    SEND_PRIORITY: bool = False            
    SEND_COMPONENTS: bool = False         

    # Swagger placeholder guard
    IGNORE_PLACEHOLDER_LITERAL: str = "string"

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
