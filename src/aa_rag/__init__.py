import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
from aa_rag.settings import setting
from .main import startup

__all__ = ["startup", "setting"]
