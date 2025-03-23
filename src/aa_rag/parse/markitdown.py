from os import PathLike
from pathlib import Path
from typing import Literal

from langchain_core.documents import Document
from markitdown import MarkItDown
from openai import OpenAI

from aa_rag import setting
from aa_rag.gtypes.enums import ParsingType
from aa_rag.oss import OSSResourceInfo
from aa_rag.parse.base import BaseParser


class MarkitDownParser(BaseParser):
    def __init__(
        self,
        use_cache: bool = True,
        update_cache: bool = True,
        llm: str = setting.llm.multimodal_model,
        **kwargs,
    ):
        """
        Initialize the MarkitDownParser with cache options and LLM settings.

        Args:
            use_cache (bool, optional): Whether to use cache. Defaults to True.
            update_cache (bool, optional): Whether to update cache. Defaults to True.
            llm (str, optional): The LLM model to use. Defaults to setting.llm.multimodal_model.
            **kwargs: Additional keyword arguments.
        """
        self.mtd_client = MarkItDown(
            llm_client=OpenAI(
                base_url=setting.openai.base_url, api_key=setting.openai.api_key
            ),
            llm_model=llm,
        )

        super().__init__(use_cache=use_cache, update_cache=update_cache)

    def type(self):
        """
        Return the type of the parser.

        Returns:
            ParsingType: The type of the parser.
        """
        return ParsingType.MARKITDOWN

    def _parse_file(
        self,
        file_path: PathLike,
        source: Literal["local", "oss"],
        oss_resource_info: OSSResourceInfo = None,
        **kwargs,
    ) -> Document:
        """
        Parse a file into a Document.

        Args:
            file_path (PathLike): The file path to parse.
            source (Literal["local", "oss"]): The source of the file.
            oss_resource_info (OSSResourceInfo): The OSS resource info. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            Document: The parsed document.
        """
        if Path(file_path).suffix in [".md"]:
            with open(file_path, mode="r") as file:
                content_str = file.read()
        else:
            content_str = self.mtd_client.convert(str(file_path)).text_content

        if source == "oss":
            return Document(
                page_content=content_str,
                metadata={
                    "source": f"{source}://{oss_resource_info.source_file_path}",
                    "oss_info": oss_resource_info.model_dump(
                        exclude={
                            "url",
                            "suffix",
                        }
                    ),
                },
            )
        else:
            return Document(
                page_content=content_str, metadata={"source": f"{source}://{file_path}"}
            )

    def _parse_content(self, content: str, **kwargs) -> Document:
        """
        Parse content into a Document.

        Args:
            content (str): The content to parse.
            **kwargs: Additional keyword arguments.

        Returns:
            Document: The parsed document.
        """
        return Document(page_content=content)
