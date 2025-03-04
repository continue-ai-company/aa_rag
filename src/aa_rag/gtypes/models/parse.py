from os import PathLike
from typing import Optional

from pydantic import Field

from aa_rag.gtypes.enums import ParsingType
from aa_rag.oss import OSSStoreInitParams


class ParserNeedItem(OSSStoreInitParams):
    file_path: Optional[PathLike] = Field(
        default=None,
        examples=[
            "user_manual/call_llm.md",
        ],
        description="Path to the file to be indexed. The file can from local file or OSS. Attention: The file_path and content cannot be both None.",
    )

    content: Optional[str] = Field(
        default=None,
        examples=[
            "# Call LLM\n\n## Introduction\n\nThis is a user manual for calling LLM.",
        ],
        description="The content to be indexed. Attention: The file_path and content cannot be both None",
    )

    parsing_type: ParsingType = Field(
        default=ParsingType.MARKITDOWN, description="The parsing type of the content."
    )

    # # Custom validator to ensure file_path and content are not both None
    # @model_validator(mode="after")
    # def check_file_path_or_content(self):
    #     # Check if both file_path and content are None
    #     if self.file_path is None and self.content is None:
    #         raise ValueError("Either file_path or content must be provided.")
    #
    #     return self    # # Custom validator to ensure file_path and content are not both None
    # @model_validator(mode="after")
    # def check_file_path_or_content(self):
    #     # Check if both file_path and content are None
    #     if self.file_path is None and self.content is None:
    #         raise ValueError("Either file_path or content must be provided.")
    #
    #     return self
