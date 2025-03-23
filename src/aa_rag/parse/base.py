import asyncio
import os
import tempfile
from abc import abstractmethod
from os import PathLike
from pathlib import Path
from typing import Iterable, List, Union, Dict, Literal

import aiohttp
import requests
from langchain_core.documents import Document

from aa_rag.oss import OSSStore, OSSStoreInitParams, OSSResourceInfo


class BaseParser(OSSStore):
    def __init__(self, use_cache: bool = True, update_cache: bool = True):
        """
        Initialize the BaseParser with OSS settings and cache options.

        Args:
            use_cache (bool, optional): Whether to use cache. Defaults to True.
            update_cache (bool, optional): Whether to update cache. Defaults to True.
        """

        super().__init__(
            OSSStoreInitParams(use_cache=use_cache, update_cache=update_cache)
        )

    @property
    def type(self):
        """
        Return the type of the parser. Must be implemented by subclasses.

        Returns:
            NotImplemented: This method should be overridden by subclasses.
        """
        return NotImplemented

    def parse(
        self,
        file_path: PathLike | Iterable[PathLike] = None,
        content: str | Iterable[str] = None,
        file_path_extra_kwargs: Dict = None,
        **kwargs,
    ) -> List[Document]:
        """
        Parse the provided file path(s) or content into a list of documents.

        Args:
            file_path (PathLike | Iterable[PathLike], optional): The file path(s) to parse. Defaults to None.
            content (str | Iterable[str], optional): The content to parse. Defaults to None.
            file_path_extra_kwargs (Dict, optional): Additional keyword arguments for each file path. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            List[Document]: A list of parsed documents.
        """
        assert file_path or content, "Either file_path or content must be provided."

        file_path_extra_kwargs = file_path_extra_kwargs or {}

        result: List[Document] = []

        if file_path:
            # file_path handling
            if isinstance(file_path, PathLike):
                file_path = [file_path]
            for _ in file_path:
                curr_uri: PathLike | OSSResourceInfo = self.check_file_path(
                    _, **file_path_extra_kwargs.get(_, {})
                )
                if isinstance(curr_uri, OSSResourceInfo):
                    with tempfile.NamedTemporaryFile(
                        delete=True, mode="wb", suffix=curr_uri.suffix
                    ) as temp_file:
                        response = requests.get(str(curr_uri.url), stream=True)
                        response.raise_for_status()

                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                temp_file.write(chunk)

                        temp_file.flush()
                        os.fsync(temp_file.fileno())

                        temp_file.seek(0)

                        result.append(
                            self._parse_file(
                                Path(temp_file.name),
                                source="oss",
                                oss_resource_info=curr_uri,
                                **kwargs,
                            )
                        )

                    # update cache handling
                    if self.update_cache:
                        if not curr_uri.hit_cache:
                            self.oss_client.put_object(
                                Bucket=self.oss_cache_bucket,
                                Key=str(
                                    Path(curr_uri.cache_file_path).relative_to(
                                        self.oss_cache_bucket
                                    )
                                )
                                if curr_uri.cache_file_path.startswith(
                                    self.oss_cache_bucket
                                )
                                else curr_uri.cache_file_path,
                                Body=result[-1].page_content,
                            )

                elif isinstance(curr_uri, Path):
                    result.append(self._parse_file(curr_uri, source="local", **kwargs))

        if content:
            # content handling
            if isinstance(content, str):
                content = [content]
            for _ in content:
                result.append(self._parse_content(_, **kwargs))

        return result

    async def aparse(
        self,
        file_path: Union[PathLike, Iterable[PathLike]] = None,
        content: Union[str, Iterable[str]] = None,
        file_path_extra_kwargs: Dict = None,
        **kwargs,
    ) -> List[Document]:
        """
        Asynchronously parse the provided file path(s) or content into a list of documents.

        Args:
            file_path (Union[PathLike, Iterable[PathLike]], optional): The file path(s) to parse. Defaults to None.
            content (Union[str, Iterable[str]], optional): The content to parse. Defaults to None.
            file_path_extra_kwargs (Dict, optional): Additional keyword arguments for each file path. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            List[Document]: A list of parsed documents.
        """

        file_path_extra_kwargs = file_path_extra_kwargs or {}

        result: List[Document] = []

        if file_path:
            if isinstance(file_path, PathLike):
                file_path = [file_path]

            async def process_path(path):
                curr_uri = self.check_file_path(
                    path, **file_path_extra_kwargs.get(path, {})
                )
                if isinstance(curr_uri, OSSResourceInfo):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(str(curr_uri.url)) as response:
                            url_content = await response.read()
                            with tempfile.NamedTemporaryFile(
                                delete=True, mode="wb", suffix=curr_uri.suffix
                            ) as temp_file:
                                temp_file.write(url_content)
                                temp_file.flush()

                                # update cache handling
                                if self.update_cache:
                                    if not curr_uri.hit_cache:
                                        self.oss_client.put_object(
                                            Bucket=self.oss_cache_bucket,
                                            Key=str(
                                                Path(
                                                    curr_uri.cache_file_path
                                                ).relative_to(self.oss_cache_bucket)
                                            )
                                            if curr_uri.cache_file_path.startswith(
                                                self.oss_cache_bucket
                                            )
                                            else curr_uri.cache_file_path,
                                            Body=url_content.decode("utf8"),
                                        )

                                return self._parse_file(
                                    Path(temp_file.name),
                                    source="oss",
                                    oss_resource_info=curr_uri,
                                    **kwargs,
                                )

                elif isinstance(curr_uri, Path):
                    return self._parse_file(curr_uri, source="local", **kwargs)

            result += await asyncio.gather(*[process_path(p) for p in file_path])

        if content:
            if isinstance(content, str):
                content = [content]
            result += [self._parse_content(c, **kwargs) for c in content]

        return result

    @abstractmethod
    def _parse_file(
        self,
        file_path: PathLike,
        source: Literal["local", "oss"],
        oss_resource_info: OSSResourceInfo = None,
        **kwargs,
    ) -> Document:
        """
        Abstract method to parse a file. Must be implemented by subclasses.

        Args:
            file_path (PathLike): The file path to parse.
            source (Literal["local", "oss"]): The source of the file.
            oss_resource_info (OSSResourceInfo): The OSS resource info.
            **kwargs: Additional keyword arguments.

        Returns:
            Document: The parsed document.
        """
        return NotImplemented

    @abstractmethod
    def _parse_content(
        self, content: str, source: Literal["local", "oss"], **kwargs
    ) -> Document:
        """
        Abstract method to parse content. Must be implemented by subclasses.

        Args:
            content (str): The content to parse.
            source (Literal["local", "oss"]): The source of the content.
            **kwargs: Additional keyword arguments.

        Returns:
            Document: The parsed document.
        """
        return NotImplemented
