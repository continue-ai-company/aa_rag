from typing import List, Any, Dict

from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from aa_rag import setting
from aa_rag.engine.simple_chunk import (
    SimpleChunk,
    SimpleChunkInitParams,
    SimpleChunkIndexParams,
    SimpleChunkRetrieveParams,
)
from aa_rag.gtypes.enums import VectorDBType
from aa_rag.knowledge_base.base import BaseKnowledge


class QAKnowledge(BaseKnowledge):
    def __init__(
        self,
        vector_db: VectorDBType = setting.storage.vector,
        **kwargs,
    ):
        """
        QA Knowledge Base. Built-in Knowledge Base.
        """
        super().__init__(**kwargs)

        # define table schema
        if vector_db == VectorDBType.LANCE:
            import pyarrow as pa

            schema = pa.schema(
                [
                    pa.field("id", pa.utf8(), False),
                    pa.field("vector", pa.list_(pa.float64(), self.dimensions), False),
                    pa.field("text", pa.utf8(), False),
                    pa.field(
                        "metadata",
                        pa.struct(
                            [
                                pa.field("solution", pa.utf8(), False),
                                pa.field("tags", pa.list_(pa.utf8()), False),
                            ]
                        ),
                        False,
                    ),
                ]
            )
        else:
            schema = None

        self.engine = SimpleChunk(
            params=SimpleChunkInitParams(knowledge_name=self.knowledge_name.lower()),
            db_type=vector_db,
            schema=schema,
        )
        self.db = vector_db

    @property
    def knowledge_name(self):
        return "QA"

    def index(self, error_desc: str, error_solution: str, tags: List[str], **kwargs):
        """
        Index the QA information.
        Args:
            error_desc: The error description.
            error_solution: The solution of the QA.
            tags: The tags of the QA.
            **kwargs:
        # check if the project is already indexed
        """

        chunk_size = (
            len(error_desc) * 2 if kwargs.get("chunk_size") is None else kwargs.get("chunk_size")
        )  # ensure the chunk size is large enough to cover the whole text. do not split the text.
        chunk_overlap = 0 if kwargs.get("chunk_overlap") is None else kwargs.get("chunk_overlap")

        self.engine.index(
            params=SimpleChunkIndexParams(
                source_data=Document(
                    page_content=error_desc,
                    metadata={"solution": error_solution, "tags": tags},
                ),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )

    def retrieve(self, error_desc: str, tags: List[str] | None = None) -> List[Any]:
        """
        Retrieve the QA information.
        Args:
            error_desc: The error description.
            tags: The tags of the QA.
        Returns:
            List[Any]: The QA information.
        """
        result = self.engine.retrieve(SimpleChunkRetrieveParams(query=error_desc))

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant. I will provide you with a query question and some retrieved documents. Identify retrieved documents that are obviously not related to the query question.
                    --Explains--
                    1. The query question and documents should be in a json format. 
                    2. The query question should be in the "query" field and the documents should be in the "documents" field.
                    3. The "documents" field should be in a list format. Each document should have an "id" field, an "error_desc" field.
                    
                    --Steps--
                    1. Identify the languages for query question and documents.error_desc.
                    2. Use the language of documents.error_desc to translate the query question if the languages are different. 
                    3. Use the translated query question to judge the retrieved document whether related to query question obviously based on "error_desc" field.
                    2. If you think have found the document that obviously unrelated retrieved documents, please return the "id" field of the document.
                    3. Do not return other information except the "id" field or language.
                    4. Please strictly follow the steps.
                    
                    
                    --Example 1--
                    -Input-
                    {{"query":"代理错误","documents":[{{"id":"1","error_desc":"网络错误，无法连接 google"}},{{"id":"2","error_desc":"windows ping不通 https://www.baidu.com"}}]}}
                    
                    -Output-
                    {{"id":[],"language":{{"query":"zh","error_desc":"zh"}}}}
                    
                    --Example 2--
                    -Input-
                    {{"query":"红烧肉太甜了","documents":[{{"id":"1","error_desc":"网络错误，无法连接 google"}},{{"id":"2","error_desc":"windows ping不通 https://www.baidu.com"}}]}}
                    
                    -Output-
                    {{"id":["1","2"],"language":{{"query":"zh","error_desc":"zh"}}}}
                    
                    --Example 3--
                    -Input-
                    {{"query":"proxy is error caused can not to navigate network?","documents":[{{"id":"1","error_desc":"网络错误，无法连接 google"}},{{"id":"2","error_desc":"windows ping不通 https://www.baidu.com"}}]}}
                    
                    -Output-
                    {{"id":[],"language":{{"query":"en","error_desc":"zh"}}}}
                    
                    --Real--
                    -Input-
                    {info_json}
                    
                    -Output-
                    
                    """,
                )
            ]
        )

        info_dict: Dict[str, Any] = dict()
        info_dict["query"] = error_desc
        info_dict["documents"] = list()
        for id_, each_result in enumerate(result):
            info_dict["documents"].append(
                {
                    "id": str(id_),
                    "error_desc": each_result["page_content"],
                    # "tags": each_result["metadata"]["tags"],
                }
            )

        chain = prompt_template | self.llm | JsonOutputParser()

        hit_doc_id_s = chain.invoke({"info_json": info_dict})

        final_result = []
        for id_, each_result in enumerate(result):
            if str(id_) not in hit_doc_id_s.get("id", []):
                final_result.append(each_result)
        return final_result
