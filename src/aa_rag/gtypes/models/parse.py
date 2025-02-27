from os import PathLike
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator

from aa_rag import setting


class OSSResourceInfo(BaseModel):
    url: HttpUrl = Field(..., description="A temp url from oss.")
    source_file_path: str = Field(..., description="The source file name.")
    hit_cache: bool = Field(..., description="Whether the url is from cache.")
    cache_file_path: str = Field(None, description="The cache file name.")
    version_id: str = Field(
        None,
        description="The version id of the file. If hit cache, the version id belong cache file, otherwise, source file.",
    )
    suffix: Optional[str] = Field(None, description="The suffix of the file.")

    @model_validator(mode="after")
    def check(self):
        if self.hit_cache:
            assert self.cache_file_path, (
                "The cache_file_path must be provided when hit_cache is True."
            )

        if self.suffix is None:
            self.suffix = Path(self.url.path).suffix

        if not self.source_file_path.startswith(setting.oss.bucket):
            self.source_file_path = f"{setting.oss.bucket}/{self.source_file_path}"
        if not self.cache_file_path.startswith(setting.oss.cache_bucket):
            self.cache_file_path = f"{setting.oss.cache_bucket}/{self.cache_file_path}"

        return self


class ParserNeedItem(BaseModel):
    file_path: Optional[PathLike] = Field(
        default=None,
        examples=[
            "user_manual/call_llm.md",
        ],
        description="Path to the file to be indexed. The file can from local file or OSS. Attention: The file_path and content cannot be both None or both provided.",
    )

    content: Optional[str] = Field(
        default=None,
        examples=[
            "# Call LLM\n\n## Introduction\n\nThis is a user manual for calling LLM. Attention: The file_path and content cannot be both None or both provided.",
        ],
        description="The content to be indexed.",
    )
    use_cache: bool = Field(
        default=True, examples=[True], description="Whether to use OSS cache."
    )

    update_cache: bool = Field(
        default=True,
        examples=[True],
        description="Whether updated to cache when parsing a new file or do not use cache file",
    )

    # Custom validator to ensure file_path and content are not both None
    @model_validator(mode="after")
    def check_file_path_or_content(self):
        # Check if both file_path and content are None
        if self.file_path is None and self.content is None:
            raise ValueError("Either file_path or content must be provided.")
        if self.file_path is not None and self.content is not None:
            raise ValueError("Only one of file_path or content can be provided.")
        return self
