import hashlib
import re
import uuid
from io import StringIO
from typing import List

import pandas as pd
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from aa_rag import setting
from aa_rag.db import LanceDBDataBase
from aa_rag.db.base import BaseVectorDataBase, BaseNoSQLDataBase
from aa_rag.db.milvus_ import MilvusDataBase
from aa_rag.db.mongo_ import MongoDBDataBase
from aa_rag.db.tinydb_ import TinyDBDataBase
from aa_rag.gtypes.enums import VectorDBType, NoSQLDBType, ParsingType
from aa_rag.gtypes.models.parse import ParserNeedItem
from aa_rag.parse.markitdown import MarkitDownParser


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
        api_key=setting.openai.api_key.get_secret_value(),
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


async def parse_content(params: ParserNeedItem) -> List[Document]:
    if params.parsing_type == ParsingType.MARKITDOWN:
        parser = MarkitDownParser()
        source_data = await parser.aparse(
            **ParserNeedItem(**params.model_dump(exclude={"parsing_type"})).model_dump()
        )
    else:
        raise ValueError(f"Invalid parsing type: {params.parsing_type}")

    return source_data


def markdown_extract_csv_df(markdown_content):
    """将 Markdown 中的 CSV 内容转换为多个 DataFrame"""

    def extract_csv_sections(markdown_content):
        """从固定格式的 Markdown 中提取三个 CSV 部分"""
        # 定义正则表达式模式（注意 re.DOTALL 允许跨行匹配）
        pattern = re.compile(
            r"-----Entities-----\s*```csv\s*(.*?)\s*```"
            r".*?"
            r"-----Relationships-----\s*```csv\s*(.*?)\s*```"
            r".*?"
            r"-----Sources-----\s*```csv\s*(.*?)\s*```",
            re.DOTALL,
        )

        # 匹配并提取内容
        match = pattern.search(markdown_content)

        # 返回包含三个 CSV 内容的字典
        return (
            {
                "entities": match.group(1).strip() if match else "",
                "relationships": match.group(2).strip() if match else "",
                "sources": match.group(3).strip() if match else "",
            }
            if match
            else {}
        )

    # 提取原始 CSV 字符串
    raw_sections = extract_csv_sections(markdown_content)

    # 结果容器
    dfs = {}

    raw_sections.pop("sources")  # 移除 sources 部分

    # 处理每个 CSV 部分
    for section_name, csv_content in raw_sections.items():
        csv_content = csv_content.replace("\t", "")
        # 处理包含多行文本的特殊字段
        dfs[section_name] = pd.read_csv(
            StringIO(csv_content),
            escapechar="\\",  # 处理转义字符
            quotechar='"',  # 识别带逗号的字段
            skipinitialspace=True,
            on_bad_lines="warn",
        )

    return dfs["entities"], dfs["relationships"]
