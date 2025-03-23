from configparser import ConfigParser
from typing import List, Union, Literal, Dict

from langchain_core.documents import Document
from pydantic import BaseModel, Field, SecretStr

from aa_rag import setting, utils
from aa_rag.db.base import BaseNoSQLDataBase
from aa_rag.engine.base import BaseEngine, BaseIndexParams
from aa_rag.gtypes.enums import EngineType

dfs_setting = setting.engine.lightrag


# 参数模型定义
class LightRAGInitParams(BaseModel):
    knowledge_name: str = Field(..., description="The name of the knowledge")
    identifier: str = Field(
        default="common", description="The identifier of the knowledge"
    )

    llm: str = Field(default=dfs_setting.llm, description="The language model to use.")


class LightRAGIndexParams(BaseIndexParams):
    source_data: Union[Document, List[Document]] = Field(
        ..., description="The source data to index."
    )


class LightRAGRetrieveParams(BaseModel):
    query: str = Field(..., description="The query string to retrieve.")
    retrieve_mode: Literal["local", "global", "hybrid", "naive", "mix"] = "hybrid"
    """Specifies the retrieval mode:
    - "local": Focuses on context-dependent information.
    - "global": Utilizes global knowledge.
    - "hybrid": Combines local and global retrieval methods.
    - "naive": Performs a basic search without advanced techniques.
    - "mix": Integrates knowledge graph and vector retrieval.
    """
    top_k: int = Field(
        default=dfs_setting.k,
        description="Number of top items to retrieve. Represents entities in 'local' mode and relationships in 'global' mode.",
    )


class LightRAGGenerateParams(BaseModel):
    pass


class LightRAGEngine(
    BaseEngine[LightRAGIndexParams, LightRAGRetrieveParams, LightRAGGenerateParams]
):
    def __init__(
        self,
        params: LightRAGInitParams,
        embedding_model: str = dfs_setting.embedding.model,
        **kwargs,
    ):
        namespace_prefix = (
            f"{params.knowledge_name}_{embedding_model}_{params.identifier}".replace(
                "-", "_"
            )
        )

        self._generate_ini_config_file()  # !! generate config.ini file because lightrag do not support specifying config file path

        from lightrag import LightRAG
        from lightrag.llm.openai import openai_embed
        from lightrag.llm.openai import openai_complete

        self.rag = LightRAG(
            working_dir=dfs_setting.dir,
            embedding_func=openai_embed,
            llm_model_name=params.llm,
            llm_model_func=openai_complete,
            namespace_prefix=namespace_prefix,
            addon_params={}
            if kwargs.get("addon_params") is None
            else kwargs.get("addon_params"),
            vector_storage=dfs_setting.vector_storage.value,
            graph_storage=dfs_setting.graph_storage.value,
            vector_db_storage_cls_kwargs={
                "cosine_better_than_threshold": dfs_setting.cosine_threshold
            },
            log_level=10,  # DEBUG Level
        )

        # get nosql obj to store the source data
        self.db: BaseNoSQLDataBase = utils.get_nosql_db(setting.storage.nosql)
        self.table_name = namespace_prefix

    @property
    def type(self):
        """
        Return the type of the engine.
        """
        return EngineType.LightRAG

    @staticmethod
    def _generate_ini_config_file():
        config = ConfigParser()

        milvus_config_dict = setting.storage.milvus.model_dump()
        config.add_section("milvus")
        for k, v in milvus_config_dict.items():
            if v:
                if isinstance(v, SecretStr):
                    v = v.get_secret_value()
                if k == "db_name":
                    v = v + "_lightrag"
                config.set("milvus", k, v)

        neo4j_config_dict = setting.storage.neo4j.model_dump()
        config.add_section("neo4j")
        for k, v in neo4j_config_dict.items():
            if v:
                if isinstance(v, SecretStr):
                    v = v.get_secret_value()
                config.set("neo4j", k, v)

        with open("config.ini", "w") as f:
            config.write(f)

    async def index(self, params: LightRAGIndexParams):
        if self.table_name not in self.db.table_list():
            self.db.create_table(self.table_name)

        id_s = []

        with self.db.using(self.table_name) as table:
            docs = (
                [params.source_data]
                if isinstance(params.source_data, Document)
                else params.source_data
            )
            for doc in docs:
                doc_id = utils.calculate_md5(doc.page_content)
                id_s.append(doc_id)
                table.insert({"doc_id": doc_id, **doc.model_dump()})

        await self.rag.ainsert(input=[doc.page_content for doc in docs], ids=id_s)

    async def retrieve(self, params: LightRAGRetrieveParams):
        from lightrag import QueryParam

        context_str = await self.rag.aquery(
            query=params.query,
            param=QueryParam(
                mode=params.retrieve_mode, only_need_context=True, top_k=params.top_k
            ),
        )
        entity_df, rel_df = utils.markdown_extract_csv_df(context_str)

        metadata_s = await self._get_doc_metadata(entity_df, rel_df)

        return [
            Document(
                page_content=context_str,
                metadata={"source": metadata_s},
            )
        ]

    def generate(self, params: LightRAGGenerateParams):
        pass

    async def _get_doc_metadata(self, entity_df, rel_df) -> List[Dict]:
        chunk_id_s = set()
        metadata_s: List = list()  # file source
        for entity in entity_df["entity"].values:
            entity: str = entity.strip().replace("'", "").replace('"', "")
            entity_info = await self.rag.get_entity_info(entity)
            if entity_info:
                source_info = await self.rag.text_chunks.get_by_id(
                    entity_info["source_id"]
                )
                if source_info:
                    chunk_id_s.add(source_info["full_doc_id"])

        for _, rel in rel_df.iterrows():
            source: str = rel["source"].strip().replace("'", "").replace('"', "")
            target: str = rel["target"].strip().replace("'", "").replace('"', "")
            rel_info = await self.rag.get_relation_info(source, target)
            if rel_info["source_id"]:
                source_info = await self.rag.text_chunks.get_by_id(
                    rel_info["source_id"]
                )
                if source_info:
                    chunk_id_s.add(source_info["full_doc_id"])

        with self.db.using(self.table_name) as table:
            docs: List[Dict] = table.select(query={"doc_id": {"$in": list(chunk_id_s)}})
            metadata_s.append(doc.get("metadata") for doc in docs)
            if None in metadata_s:
                metadata_s.remove(None)

        return metadata_s
