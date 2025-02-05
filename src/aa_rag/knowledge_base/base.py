from typing import Any, List

from aa_rag import setting, utils


class BaseKnowledge:
    _knowledge_name: str

    def __init__(
        self,
        llm: str = setting.llm.model,
        embedding_model: str = setting.embedding.model,
        **kwargs,
    ):
        self.llm = utils.get_llm(llm)
        self.embedding_model = utils.get_embedding_model(embedding_model)

    @property
    def knowledge_name(self):
        return self._knowledge_name

    def index(self, **kwargs):
        return NotImplemented

    def retrieve(self, **kwargs) -> List[Any]:
        return NotImplemented
