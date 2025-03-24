from typing import Any, Optional, List

from pydantic import BaseModel, Field, AnyUrl, ConfigDict

from aa_rag.gtypes.models.base import BaseResponse
from aa_rag.gtypes.models.knowlege_base.base import BaseKnowledgeItem


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
    id: Optional[str] = Field(None, description="Project ID")
    description: Optional[str] = Field(None, description="Project description")
    git_url: Optional[AnyUrl] = Field(None, description="Git URL of the project")
    guides: Optional[List[Guide]] = Field(
        None, description="The deployment guide of the project"
    )


class SolutionIndexItem(BaseKnowledgeItem):
    env_info: CompatibleEnv = Field(..., description="The environment information")
    procedure: str = Field(..., description="The deployment procedure of the solution")

    class Project_Meta(BaseModel):
        name: str = Field(..., description="Project name")
        model_config = ConfigDict(extra="allow")

    project_meta: Project_Meta = Field(..., description="The project meta information")


class SolutionRetrieveItem(BaseKnowledgeItem):
    env_info: CompatibleEnv = Field(..., description="The environment information")
    project_meta: SolutionIndexItem.Project_Meta = Field(
        ..., description="The project meta information"
    )


class SolutionIndexResponse(BaseResponse):
    default_response_code: int = Field(default=201, exclude=True)
    message: str = Field(
        default="Indexing completed in Solution Knowledge Base",
        examples=["Indexing completed in Solution Knowledge Base"],
    )


class SolutionRetrieveResponse(BaseResponse):
    message: str = Field(
        default="Retrieval completed in Solution Knowledge Base",
        examples=["Retrieval completed in Solution Knowledge Base"],
    )
