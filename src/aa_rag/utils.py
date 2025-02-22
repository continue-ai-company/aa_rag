import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from markitdown import MarkItDown
from openai import OpenAI

from aa_rag import setting
from aa_rag.db import LanceDBDataBase
from aa_rag.db.base import BaseVectorDataBase, BaseNoSQLDataBase
from aa_rag.db.milvus_ import MilvusDataBase
from aa_rag.db.mongo_ import MongoDBDataBase
from aa_rag.db.tinydb_ import TinyDBDataBase
from aa_rag.gtypes.enums import VectorDBType, NoSQLDBType

s3_client: Any = None
md_parser = MarkItDown(
    llm_client=OpenAI(base_url=setting.openai.base_url, api_key=setting.openai.api_key),
    llm_model=setting.llm.model,
)


def parse_file(
    file_path: str,
    use_cache: bool = True,
    version_id="",
    cache_version_id="",
) -> Document:
    """
    Parse a file to MarkDown string and return a Document object.

    Args:
        file_path (str): Path to the file to be parsed. The file path can from the local file system or oss service. Local files are parsed first.
        use_cache (bool): Use cache for the parsed content. This parameter only works for oss service.
        version_id (str): Version ID for the file. This parameter only works for oss service.
        cache_version_id (str): Version ID for the cache file. This parameter only works for oss service.

    Returns:
        Document: Document object containing the parsed content and metadata.
    """
    file_path = Path(file_path)
    if file_path.exists():  # check if the file exists in the local file system
        if file_path.suffix in [".md"]:
            with open(file_path, "r") as f:
                content_str = f.read()
        else:
            content_str = md_parser.convert(str(file_path.absolute())).text_content
    elif setting.oss.access_key and setting.oss.secret_key:
        try:
            import boto3
            from botocore.exceptions import ClientError

            global s3_client
            s3_client = (
                boto3.client(
                    "s3",
                    endpoint_url=setting.oss.endpoint,
                    aws_access_key_id=setting.oss.access_key,
                    aws_secret_access_key=setting.oss.secret_key,
                    use_ssl=False
                    if setting.oss.endpoint.startswith("http://")
                    else True,
                    verify=False
                    if setting.oss.endpoint.startswith("http://")
                    else True,
                )
                if not s3_client
                else s3_client
            )
            try:
                s3_client.head_bucket(Bucket=setting.oss.bucket)
            except ClientError:
                raise FileNotFoundError(
                    f"Bucket not found: {setting.oss.bucket} in oss service."
                )
            try:
                obj_info = s3_client.head_object(
                    Bucket=setting.oss.bucket,
                    Key=str(file_path),
                    VersionId=version_id,
                )
                md5_value = obj_info["ETag"].replace('"', "")
                cache_file_path = f"parsed_{md5_value}.md"
            except ClientError:
                raise FileNotFoundError(
                    f"File not found: {file_path} in bucket: {setting.oss.bucket}"
                )

            have_cache_bucket = have_cache_file = False
            # cache operation
            try:
                s3_client.head_bucket(Bucket=setting.oss.cache_bucket)
                have_cache_bucket = True
            except ClientError as e:
                logging.warning(f"Cache bucket check failed: {e}. Disabling cache.")

            if have_cache_bucket and use_cache:
                try:
                    s3_client.head_object(
                        Bucket=setting.oss.cache_bucket,
                        Key=cache_file_path,
                        VersionId=cache_version_id,
                    )
                    have_cache_file = True
                except ClientError as e:
                    logging.warning(f"Cache file check failed: {e}. Disabling cache.")

                if have_cache_bucket and have_cache_file:
                    target_bucket, target_file_path, target_version_id = (
                        setting.oss.cache_bucket,
                        Path(cache_file_path),
                        cache_version_id,
                    )
                else:
                    target_bucket, target_file_path, target_version_id = (
                        setting.oss.bucket,
                        file_path,
                        version_id,
                    )
            else:
                target_bucket, target_file_path, target_version_id = (
                    setting.oss.bucket,
                    file_path,
                    version_id,
                )

            if target_file_path.suffix in [".md"]:
                content_str = (
                    s3_client.get_object(
                        Bucket=target_bucket,
                        Key=str(target_file_path),
                        VersionId=target_version_id,
                    )["Body"]
                    .read()
                    .decode("utf-8")
                )
            else:
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": target_bucket,
                        "Key": str(target_file_path),
                        "VersionId": target_version_id,
                    }
                    if target_version_id
                    else {
                        "Bucket": target_bucket,
                        "Key": str(target_file_path),
                    },
                )

                convert_result = md_parser.convert(url)
                content_str = convert_result.text_content

            if have_cache_bucket and not have_cache_file:
                s3_client.put_object(
                    Bucket=setting.oss.cache_bucket,
                    Key=cache_file_path,
                    Body=content_str,
                )

        except ImportError:
            raise FileNotFoundError(
                f'File not found: {file_path} in local file system. If the file in the oss service, please enable the online service. You can execute `pip install "aa-rag[online]"` first.'
            )
    else:
        raise FileNotFoundError(
            f"File not found: {file_path} in local file system or oss service."
        )

    return Document(page_content=content_str, metadata={"source": file_path.name})


def calculate_md5(input_string: str) -> str:
    """
    Calculate the MD5 hash of a string.

    Args:
        input_string (str): need to be calculated.

    Returns:
        str: MD5 hash of the input string.
    """
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode("utf-8"))
    return md5_hash.hexdigest()


def get_embedding_model(
    model_name: str, return_dim: bool = False
) -> Embeddings | tuple[Embeddings, int]:
    """
    Get the embedding model based on the model name.
    Args:
        model_name (str): Model name.
        return_dim (bool): Return the embedding dimension if True.

    Returns:
        Embeddings: Embedding model instance.
        If return_dim is True, also returns the number of dimensions.

    """
    assert setting.openai.api_key, (
        "OpenAI API key is required for using OpenAI embeddings."
    )
    embeddings = OpenAIEmbeddings(
        model=model_name,
        dimensions=1536,
        api_key=setting.openai.api_key,
        base_url=setting.openai.base_url,
    )
    if return_dim:
        return embeddings, embeddings.dimensions or 1536
    else:
        return embeddings


def get_llm(model_name: str) -> BaseChatModel:
    assert setting.openai.api_key, (
        "OpenAI API key is required for using OpenAI embeddings."
    )
    model = ChatOpenAI(
        model=model_name,
        api_key=setting.openai.api_key,
        base_url=setting.openai.base_url,
    )

    return model


def get_vector_db(db_type: VectorDBType) -> BaseVectorDataBase | None:
    match db_type:
        case VectorDBType.LANCE:
            return LanceDBDataBase()
        case VectorDBType.MILVUS:
            return MilvusDataBase()
        case _:
            raise ValueError(f"Invalid db type: {db_type}")


def get_nosql_db(db_type: NoSQLDBType) -> BaseNoSQLDataBase | None:
    match db_type:
        case NoSQLDBType.TINYDB:
            return TinyDBDataBase()
        case NoSQLDBType.MONGODB:
            return MongoDBDataBase()
        case _:
            raise ValueError(f"Invalid db type: {db_type}")


def get_db(
    db_type: NoSQLDBType | VectorDBType,
) -> BaseNoSQLDataBase | BaseVectorDataBase | None:
    if isinstance(db_type, NoSQLDBType):
        return get_nosql_db(db_type)
    elif isinstance(db_type, VectorDBType):
        return get_vector_db(db_type)
    else:
        raise ValueError(f"Invalid db type: {db_type}")


def get_uuid():
    return str(uuid.uuid4()).replace("-", "")
