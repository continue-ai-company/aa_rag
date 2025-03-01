import copy
from pathlib import Path
from typing import List, Union, Dict

from pandas import DataFrame
from pymilvus import (
    CollectionSchema,
    MilvusClient,
    DataType,
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
        uri: str = setting.storage.milvus.uri,
        user: str = setting.storage.milvus.user,
        password: str = setting.storage.milvus.password.get_secret_value(),
        db_name: str = setting.storage.milvus.db_name,
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

    @property
    def connection(self) -> MilvusClient:
        return self._conn_obj

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
        return self.connection.delete(self.using_collection_name, where, **kwargs)

    def upsert(self, data: list[dict] | DataFrame, **kwargs):
        """Upsert data into collection with JSON merge support"""
        assert self.using_collection_name, "Collection not loaded. Use using() first"

        def update_old_json_with_new(new_data):
            # 获取字段描述
            fields = self.connection.describe_collection(self.using_collection_name)[
                "fields"
            ]

            # 健壮的主键获取（修复问题4）
            primary_keys = [
                field["name"] for field in fields if field.get("is_primary", False)
            ]
            if not primary_keys:
                raise ValueError("Collection has no primary key")
            primary_key = primary_keys[0]

            json_fields = [
                field["name"] for field in fields if field["type"] == DataType.JSON
            ]

            # 获取所有需要更新的字段（修复问题3）
            all_fields = list(
                {primary_key}.union(json_fields, *[d.keys() for d in new_data])
            )

            # 构建查询表达式（修复潜在的类型问题）
            pk_values = [str(d[primary_key]) for d in new_data if primary_key in d]
            if not pk_values:
                return new_data  # 无主键直接插入新数据

            # 查询旧数据（包含所有必要字段）
            old_data = self.query(
                expr=f"{primary_key} in {pk_values}", output_fields=all_fields
            )
            old_data_map = {str(d[primary_key]): d for d in old_data}

            # 递归合并函数（修复问题2）
            def deep_merge(
                original: Union[Dict, List, None], new: Union[Dict, List]
            ) -> Union[Dict, List]:
                if original is None:
                    original = {} if isinstance(new, dict) else []
                merged = copy.deepcopy(original)
                if isinstance(merged, dict) and isinstance(new, dict):
                    for k, v in new.items():
                        if k not in merged:
                            merged[k] = copy.deepcopy(v)
                        elif isinstance(v, dict) and isinstance(merged[k], dict):
                            merged[k] = deep_merge(merged[k], v)
                        elif isinstance(v, list) and isinstance(merged[k], list):
                            merged[k] = list(set(merged[k] + v))  # 保留顺序
                        else:
                            merged[k] = v
                elif isinstance(merged, list) and isinstance(new, list):
                    merged = list(set(merged + new))
                else:
                    raise ValueError(f"Cannot merge {type(original)} with {type(new)}")
                return merged

            # 合并数据（修复问题1）
            merged_data = []
            for new_item in new_data:
                pk_value = str(new_item.get(primary_key))
                old_item = old_data_map.get(pk_value, {})

                # only merge json fields
                for field in json_fields:
                    new_item[field] = deep_merge(
                        old_item.get(field), new_item.get(field)
                    )

                merged_data.append(new_item)

            return merged_data

        # 数据格式转换
        if isinstance(data, DataFrame):
            data = data.to_dict(orient="records")

        # 执行合并逻辑
        processed_data = update_old_json_with_new(data)

        # 执行upsert
        return self.connection.upsert(
            collection_name=self.using_collection_name, data=processed_data
        )

    def overwrite(self, data: list[dict] | DataFrame, **kwargs):
        assert self.using_collection_name, "Collection not loaded. Use using() first"
        self.delete(where="id is not null")  # truncate collection
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
