from pathlib import Path
from typing import List

from pandas import DataFrame
from pymilvus import (
    CollectionSchema,
    MilvusClient,
)

from aa_rag import setting
from aa_rag.db.base import BaseVectorDataBase, singleton
from aa_rag.gtypes.enums import VectorDBType


@singleton
class MilvusDataBase(BaseVectorDataBase):
    """Milvus vector database implementation with unified interface"""

    _db_type = VectorDBType.MILVUS
    using_collection_name: str | None = None

    def __init__(
        self,
        uri: str = setting.db.milvus.uri,
        user: str = setting.db.milvus.user,
        password: str = setting.db.milvus.password.get_secret_value(),
        db_name: str = setting.db.milvus.database,
        **kwargs,
    ):
        # create parent directory if not exist
        if uri.startswith("http"):
            uri = uri
        else:
            Path(uri).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            uri=uri, user=user, password=password, db_name=db_name, **kwargs
        )

    def connect(self, **kwargs) -> MilvusClient:
        """Connect to Milvus server"""
        return MilvusClient(**kwargs)

    def table_list(self, **kwargs) -> List[str]:
        """List all collection names"""
        return self.connection.list_collections()

    def create_table(self, table_name: str, schema: CollectionSchema, **kwargs):
        """Create new collection with schema"""
        if table_name not in self.table_list():
            if kwargs.get("index_params"):
                self.connection.create_collection(
                    collection_name=table_name,
                    schema=schema,
                    index_params=kwargs.get("index_params"),
                )
            else:
                index_params = self.connection.prepare_index_params()
                index_params.add_index(
                    field_name="vector", index_type="AUTOINDEX", metric_type="L2"
                )
                self.connection.create_collection(
                    collection_name=table_name, schema=schema, index_params=index_params
                )
        else:
            raise ValueError(f"Collection {table_name} already exists")

    def drop_table(self, table_name: str):
        """Drop specified collection"""
        self.connection.drop_collection(table_name)

    def using(self, collection_name: str, **kwargs):
        """Set table to use"""
        self.connection.load_collection(collection_name=collection_name)
        self.using_collection_name = collection_name

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.connection.release_collection(collection_name=self.using_collection_name)
        self.using_collection_name = None
        return False

    def close(self):
        self.connection.close()

    def insert(self, data: List[dict], **kwargs):
        """Insert data into collection"""
        assert self.using_collection_name, "Collection not loaded. Use using() first"
        res = self.connection.insert(
            collection_name=self.using_collection_name, data=data
        )
        return res

    def delete(self, where: str, **kwargs):
        """Delete entities with boolean expression"""
        assert self.using_collection_name, "Collection not loaded. Use using() first"
        return self.connection.delete(
            collection_name=self.using_collection_name, filter=where, **kwargs
        )

    def upsert(self, data: list[dict] | DataFrame, **kwargs):
        """Upsert data into collection"""
        assert self.using_collection_name, "Collection not loaded. Use using() first"
        return self.connection.upsert(
            collection_name=self.using_collection_name, data=data
        )

    def overwrite(self, data: list[dict] | DataFrame, **kwargs):
        assert self.using_collection_name, "Collection not loaded. Use using() first"
        self.delete(where="")  # truncate collection
        return self.insert(data=data)

    # def search(
    #         self,
    #         query_vector: List[float],
    #         top_k: int = 3,
    #         anns_field: str = "vector",
    #         **kwargs,
    # ):
    #     """Vector similarity search"""
    #
    #     # Convert to numpy array and normalize if needed
    #     vector = np.array(query_vector, dtype=np.float32)
    #
    #     res = self.connection.search(
    #         collection_name=self.using_collection_name,
    #         anns_field=anns_field,
    #         data=[vector],
    #         limit=top_k,
    #         search_params={"metric_type": "IP"},
    #         **kwargs,
    #     )
    #
    #     return [
    #         {"id": hit.id, "distance": hit.distance, **hit.entity.to_dict()}
    #         for hit in res[0]
    #     ]

    def query(self, expr, **kwargs):
        iterator = self.connection.query_iterator(
            batch_size=1000,
            collection_name=self.using_collection_name,
            filter=expr,
            output_fields=kwargs.get("output_fields", None),
            limit=kwargs.get("limit", -1),
        )

        results = []

        while True:
            result = iterator.next()
            if not result:
                iterator.close()
                break

            results += result

        return results


if __name__ == "__main__":
    milvus_db = MilvusDataBase()
    milvus_db.connect()
    print(milvus_db.table_list())

    with milvus_db.using("user_guide_chunk_text_embedding_3_small") as db:
        milvus_db.query(
            "id in ['8672a4c387ff30688588e22f2e5e7c6c']",
            limit=10,
            output_fields=["id", "text"],
        )
