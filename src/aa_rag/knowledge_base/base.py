from abc import abstractmethod
from typing import Any, List

from aa_rag import setting, utils


class BaseKnowledge:
    dimensions: int

    def __init__(
        self,
        llm: str = setting.llm.model,
        embedding_model: str = setting.embedding.model,
        **kwargs,
    ):
        self.llm = utils.get_llm(llm)
        self.embedding_model, self.dimensions = utils.get_embedding_model(
            embedding_model, return_dim=True
        )

    @property
    @abstractmethod
    def knowledge_name(self):
        return NotImplemented

    def index(self, **kwargs):
        return NotImplemented

    def retrieve(self, **kwargs) -> List[Any]:
        return NotImplemented
