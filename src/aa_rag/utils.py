import os
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from markitdown import MarkItDown
from langchain_core.documents import Document
import hashlib

from aa_rag.gtypes.enums import EmbeddingModel


def parse_file(file_path: Path) -> Document:
    """
    Parse a file and return a Document object.

    Args:
        file_path (str): Path to the file to be parsed.

    Returns:
        Document: Document object containing the parsed content and metadata.
    """
    assert file_path.exists(), f"File not found: {file_path}"

    md = MarkItDown()
    content_str = md.convert(str(file_path.absolute())).text_content

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


def get_embedding_model(model_name: EmbeddingModel) -> Embeddings:
    """
    Get the embedding model based on the model name.
    Args:
        model_name (EmbeddingModel): Model name.

    Returns:
        Embeddings: Embedding model instance.

    """
    match model_name:
        case EmbeddingModel.TEXT_EMBEDDING_3_SMALL:
            assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is not set"
            embeddings = OpenAIEmbeddings(model=model_name.value)
        case _:
            raise ValueError(f"Invalid model name: {model_name}")
    return embeddings
