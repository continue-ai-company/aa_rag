import asyncio
import logging
import os
import tempfile
from abc import abstractmethod
from os import PathLike
from pathlib import Path
from typing import Iterable, Tuple, List, Union, Dict, Literal

import aiohttp
import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from langchain_core.documents import Document

from aa_rag import setting
from aa_rag.gtypes.models.parse import OSSResourceInfo


class BaseParser:
    _oss_available: bool
    _oss_cache_available: bool

    def __init__(
        self,
        use_cache: bool = True,
        update_cache: bool = True,
        oss_endpoint: str = setting.oss.endpoint,
        oss_bucket: str = setting.oss.bucket,
        oss_cache_bucket: str = setting.oss.cache_bucket,
        oss_access_key: str = setting.oss.access_key,
        oss_secret_key: str = setting.oss.secret_key.get_secret_value(),
    ):
        """
        Initialize the BaseParser with OSS settings and cache options.

        Args:
            use_cache (bool, optional): Whether to use cache. Defaults to True.
            update_cache (bool, optional): Whether to update cache. Defaults to True.
            oss_endpoint (str): The endpoint URL for the OSS service.
            oss_bucket (str): The name of the main OSS bucket.
            oss_cache_bucket (str): The name of the cache OSS bucket.
            oss_access_key (str): The access key for the OSS service.
            oss_secret_key (str): The secret key for the OSS service.
        """
        self._oss_available, self._oss_cache_available = self._validate_oss(
            oss_endpoint, oss_bucket, oss_cache_bucket, oss_access_key, oss_secret_key
        )

        if self.oss_available:
            self.oss_client = boto3.client(
                "s3",
                endpoint_url=oss_endpoint,
                aws_access_key_id=oss_access_key,
                aws_secret_access_key=oss_secret_key,
                use_ssl=oss_endpoint.startswith("https://"),
                verify=oss_endpoint.startswith("https://"),
            )

        else:
            self.oss_client = None

        self.oss_bucket = oss_bucket
        self.oss_cache_bucket = oss_cache_bucket
        self.use_cache = use_cache
        self.update_cache = update_cache

    @property
    def type(self):
        """
        Return the type of the parser. Must be implemented by subclasses.

        Returns:
            NotImplemented: This method should be overridden by subclasses.
        """
        return NotImplemented

    @property
    def oss_available(self):
        """
        Check if OSS is available.

        Returns:
            bool: True if OSS is available, False otherwise.
        """
        return self._oss_available

    @property
    def oss_cache_available(self):
        """
        Check if OSS cache is available.

        Returns:
            bool: True if OSS cache is available, False otherwise.
        """
        return self._oss_cache_available

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
                curr_uri: PathLike | OSSResourceInfo = self._check_file_path(
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
        assert file_path or content, "Either file_path or content must be provided."

        file_path_extra_kwargs = file_path_extra_kwargs or {}

        result: List[Document] = []

        if file_path:
            if isinstance(file_path, PathLike):
                file_path = [file_path]

            async def process_path(path):
                curr_uri = self._check_file_path(
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
                                            Body=result[-1].page_content,
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

    def _check_file_path(
        self, file_path: PathLike, **kwargs
    ) -> PathLike | OSSResourceInfo:
        """
        Check the file path and return the appropriate resource info.

        Args:
            file_path (PathLike): The file path to check.
            **kwargs: Additional keyword arguments.

        Returns:
            PathLike | OSSResourceInfo: The local file path or OSS resource info.
        """
        # find file path from local first
        if Path(file_path).exists():
            return file_path

        if self.oss_available:
            # check oss file exist
            try:
                oss_file_info = self.oss_client.head_object(
                    Bucket=setting.oss.bucket,
                    Key=str(file_path),
                    VersionId=kwargs.get("version_id", ""),
                )
            except ClientError:
                raise FileNotFoundError(
                    f"File not found: {file_path} in local and bucket: {setting.oss.bucket}"
                )

            md5_value = oss_file_info["ETag"].replace('"', "")
            cache_file_path = f"parsed_{md5_value}.md"
            if self.oss_cache_available and self.use_cache:
                # check oss cache file exist
                try:
                    cache_file_info = self.oss_client.head_object(
                        Bucket=setting.oss.cache_bucket,
                        Key=cache_file_path,
                        VersionId=kwargs.get("cache_version_id", ""),
                    )
                    target_bucket = self.oss_cache_bucket
                    target_file_path = cache_file_path
                    target_version_id = cache_file_info.get("VersionId")

                    hit_cache = True
                except ClientError:
                    target_bucket = self.oss_bucket
                    target_file_path = str(file_path)
                    target_version_id = oss_file_info.get("VersionId")

                    hit_cache = False
            else:
                target_bucket = self.oss_bucket
                target_file_path = file_path
                target_version_id = oss_file_info.get("VersionId")

                hit_cache = False

            # get temp url for file
            tmp_oss_url = self.oss_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": target_bucket,
                    "Key": target_file_path,
                    "VersionId": target_version_id,
                }
                if target_version_id
                else {
                    "Bucket": target_bucket,
                    "Key": target_file_path,
                },
            )
            return OSSResourceInfo(
                url=tmp_oss_url,
                source_file_path=str(file_path),
                cache_file_path=target_file_path if hit_cache else cache_file_path,
                hit_cache=hit_cache,
                version_id=target_version_id,
                suffix=None,
            )
        else:
            raise FileNotFoundError(f"File not found: {file_path} in local.")

    @abstractmethod
    def _parse_file(
        self,
        file_path: PathLike,
        source: Literal["local", "oss"],
        oss_resource_info: OSSResourceInfo,
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

    @staticmethod
    def _validate_oss(
        oss_endpoint: str,
        oss_bucket: str,
        oss_cache_bucket: str,
        oss_access_key: str,
        oss_secret_key: str,
    ) -> Tuple[bool, bool]:
        """
        Validate the OSS (Object Storage Service) connection and buckets.

        Args:
            oss_endpoint (str): The endpoint URL for the OSS service.
            oss_bucket (str): The name of the main OSS bucket.
            oss_cache_bucket (str): The name of the cache OSS bucket.
            oss_access_key (str): The access key for the OSS service.
            oss_secret_key (str): The secret key for the OSS service.

        Returns:
            Tuple[bool, bool]: A tuple of two boolean values. The first value indicates whether the OSS service is valid. The second value indicates whether the cache bucket is valid.
        """
        if not all([oss_access_key, oss_secret_key]):
            return False, False

        # Create S3 client
        try:
            oss_client = boto3.client(
                "s3",
                endpoint_url=oss_endpoint,
                aws_access_key_id=oss_access_key,
                aws_secret_access_key=oss_secret_key,
                use_ssl=oss_endpoint.startswith("https://"),
                verify=oss_endpoint.startswith("https://"),
            )
        except BotoCoreError as e:
            logging.warning(
                f"Failed to connect to OSS service: {str(e)}. No longer use OSS."
            )
            return False, False

        try:
            # Validate main bucket
            oss_client.head_bucket(Bucket=oss_bucket)
        except ClientError:
            logging.warning(
                f"Bucket not found: {oss_bucket} in oss service. No longer use OSS."
            )

        try:
            # Validate cache bucket
            oss_client.head_bucket(Bucket=oss_cache_bucket)
            return True, True
        except ClientError:
            logging.warning(
                f"Cache bucket not found: {oss_cache_bucket} in oss service. No longer use OSS cache."
            )
            return True, False
