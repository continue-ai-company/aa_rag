from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from markitdown import MarkItDown
from langchain_core.documents import Document
import hashlib


def parse_file(file_path: str) -> Document:
    """
    Parse a file and return a Document object.

    Args:
        file_path (str): Path to the file to be parsed.

    Returns:
        Document: Document object containing the parsed content and metadata.
    """
    file_path_obj = Path(file_path)
    assert file_path_obj.exists(), f"File not found: {file_path}"

    md = MarkItDown()
    content_str = md.convert(str(file_path_obj.absolute())).text_content

    return Document(page_content=content_str, metadata={"source": file_path_obj.name})


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


def get_embedding_model(model_name: str) -> str:
    """
    Get the path to the embedding model.

    Args:
        model_name (str): Name of the model.

    Returns:
        str: Path to the embedding model.
    """
    embeddings = OpenAIEmbeddings(model=model_name)
    return embeddings
