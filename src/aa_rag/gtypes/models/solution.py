from typing import Any, Optional, List

from pydantic import BaseModel, Field, AnyUrl, ConfigDict


class CompatibleEnv(BaseModel):
    # Platform and Operating System (required)
    platform: Any = Field(
        ..., description="The operating system platform, e.g., Darwin 24.1.0"
    )
    arch: Any = Field(..., description="The system architecture, e.g., arm64")

    model_config = ConfigDict(extra="allow")


class Guide(BaseModel):
    procedure: str = Field(
        ..., description="The detailed deployment process of the guide"
    )
    compatible_env: CompatibleEnv = Field(
        ..., description="The compatible environment of the guide"
    )


class Project(BaseModel):
    name: str = Field(..., description="Project name")
    id: Optional[int] = Field(None, description="Project ID")
    description: Optional[str] = Field(None, description="Project description")
    git_url: Optional[AnyUrl] = Field(None, description="Git URL of the project")
    guides: Optional[List[Guide]] = Field(
        None, description="The deployment guide of the project"
    )
