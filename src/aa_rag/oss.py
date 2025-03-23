import logging
from os import PathLike
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import quote

from langchain_core.documents import Document
from pydantic import BaseModel, Field, HttpUrl, model_validator

from aa_rag import setting, utils


class OSSStoreInitParams(BaseModel):
    use_cache: bool = Field(
        default=True, examples=[True], description="Whether to use OSS cache."
    )
    update_cache: bool = Field(
        default=True, examples=[True], description="Whether to update OSS cache."
    )


class OSSResourceInfo(BaseModel):
    url: Optional[HttpUrl] = Field(default=None, description="A temp url from oss.")
    source_file_path: str = Field(..., description="The source file name.")
    hit_cache: bool = Field(..., description="Whether the url is from cache.")
    cache_file_path: str = Field(default=None, description="The cache file name.")
    version_id: str = Field(
        default=None,
        description="The version id of the file. If hit cache, the version id belong cache file, otherwise, source file.",
    )
    suffix: Optional[str] = Field(default=None, description="The suffix of the file.")

    @model_validator(mode="after")
    def check(self):
        if self.hit_cache:
            assert self.cache_file_path, (
                "The cache_file_path must be provided when hit_cache is True."
            )

        if self.suffix is None and self.url is not None:
            self.suffix = Path(self.url.path).suffix

        if not self.source_file_path.startswith(setting.oss.bucket):
            self.source_file_path = f"{setting.oss.bucket}/{self.source_file_path}"
        if self.cache_file_path is not None and not self.cache_file_path.startswith(
            setting.oss.cache_bucket
        ):
            self.cache_file_path = f"{setting.oss.cache_bucket}/{self.cache_file_path}"

        return self


class OSSStore:
    from aa_rag.db.multimodal import StoreImageParams

    _oss_available: bool
    _oss_cache_available: bool

    def __init__(
        self,
        params: OSSStoreInitParams,
        oss_endpoint: str = setting.oss.endpoint,
        oss_bucket: str = setting.oss.bucket,
        oss_cache_bucket: str = setting.oss.cache_bucket,
        oss_access_key: str = setting.oss.access_key,
        oss_secret_key: str = setting.oss.secret_key.get_secret_value()
        if setting.oss.secret_key
        else None,
    ):
        """
        Initialize the BaseParser with OSS settings and cache options.

        Args:
            params(OSSStoreInitParams)
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
            import boto3

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
        self.use_cache = params.use_cache
        self.update_cache = params.update_cache

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
        from botocore.exceptions import BotoCoreError

        try:
            import boto3

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

        from botocore.exceptions import ClientError

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

    def check_file_path(
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
            return Path(file_path)

        if self.oss_available:
            # check oss file exist
            from botocore.exceptions import ClientError

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

    def store_image(self, params: StoreImageParams) -> Document:
        img_file_name, content_type, binary_data = (
            utils.convert_img_base64_to_file_info(params.image, params.img_desc)
        )
        img_file_path = f"image/{img_file_name}"

        try:
            oss_info = self.check_file_path(Path(img_file_path))
        except FileNotFoundError:
            self.oss_client.put_object(
                Bucket=self.oss_bucket,
                Key=str(Path(img_file_path)),
                Body=binary_data,
                ContentType=content_type,
                Metadata={
                    "description": quote(params.img_desc),
                },
            )
            oss_info = OSSResourceInfo(
                source_file_path=f"{self.oss_bucket}/{img_file_path}", hit_cache=False
            )

        assert isinstance(oss_info, OSSResourceInfo), (
            f"oss_info must be an instance of OSSResourceInfo, not {type(oss_info)}"
        )

        return Document(
            page_content=params.img_desc,
            metadata={
                "source": f"oss://{oss_info.source_file_path}",
                "suffix": Path(img_file_path).suffix,
            },
        )
