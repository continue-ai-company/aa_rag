from pathlib import Path

from tinydb import TinyDB, Query
from tinydb.table import Table

from aa_rag import setting
from aa_rag.db.base import BaseNoSQLDataBase


class TinyDBDataBase(BaseNoSQLDataBase):
    _db_type = "TinyDB"

    def __init__(self, uri: str = setting.db.nosql.uri, **kwargs):
        self.uri = uri
        # 如果目录不存在，则创建父目录
        Path(self.uri).parent.mkdir(parents=True, exist_ok=True)

        self._conn_obj = self.connect()
        self._table_obj = None

        super().__init__(**kwargs)

    @property
    def connection(self) -> TinyDB:
        return self._conn_obj

    @property
    def table(self) -> Table:
        if self._table_obj is None:
            raise ValueError(
                "Table 对象未定义，请先调用 `get_table(table_name)` 方法设置 table 对象"
            )
        return self._table_obj

    def connect(self):
        return TinyDB(self.uri)

    def create_table(self, table_name, **kwargs):
        """创建并返回指定名称的表"""
        return self.connection.table(table_name, **kwargs)

    def get_table(self, table_name, **kwargs):
        """设置当前使用的表，并返回 self 以支持链式调用"""
        self._table_obj = self.connection.table(table_name, **kwargs)
        return self

    def table_list(self):
        """返回所有表的名称集合"""
        return self.connection.tables()

    def drop_table(self, table_name):
        """删除指定名称的表"""
        return self.connection.drop_table(table_name)

    def insert(self, data):
        """
        插入数据。
        注意：此处 data 可以为单个 dict 或 dict 列表，根据 tinydb 的 insert/insert_multiple 方法自行扩展。
        """
        return self.table.insert(data)

    def _build_query_mongo(self, mongo_query: dict, q: Query = None):
        """
        将 MongoDB 查询语法转换为 TinyDB 的查询表达式。

        支持的 MongoDB 查询操作符包括：
          - 比较操作符: $gt, $gte, $lt, $lte, $eq, $ne
          - 集合操作符: $in, $nin
          - 存在性判断: $exists
          - 逻辑操作符: $and, $or, $nor, $not

        示例：
          {"age": {"$gt": 30, "$lt": 50}, "name": "John"}
          等价于：
          (Query()['age'] > 30) & (Query()['age'] < 50) & (Query()['name'] == "John")
        """
        if q is None:
            q = Query()
        if isinstance(mongo_query, dict):
            # 处理顶层逻辑操作符
            if "$and" in mongo_query:
                sub_exprs = [
                    self._build_query_mongo(sub, q) for sub in mongo_query["$and"]
                ]
                expr = sub_exprs[0]
                for e in sub_exprs[1:]:
                    expr = expr & e
                return expr
            elif "$or" in mongo_query:
                sub_exprs = [
                    self._build_query_mongo(sub, q) for sub in mongo_query["$or"]
                ]
                expr = sub_exprs[0]
                for e in sub_exprs[1:]:
                    expr = expr | e
                return expr
            elif "$nor" in mongo_query:
                sub_exprs = [
                    self._build_query_mongo(sub, q) for sub in mongo_query["$nor"]
                ]
                expr = sub_exprs[0]
                for e in sub_exprs[1:]:
                    expr = expr | e
                return ~expr
            elif "$not" in mongo_query:
                sub_expr = self._build_query_mongo(mongo_query["$not"], q)
                return ~sub_expr
            else:
                # 处理字段查询
                sub_exprs = []
                for field, condition in mongo_query.items():
                    if isinstance(condition, dict):
                        field_expr = None
                        for op, val in condition.items():
                            if op == "$gt":
                                current = q[field] > val
                            elif op == "$gte":
                                current = q[field] >= val
                            elif op == "$lt":
                                current = q[field] < val
                            elif op == "$lte":
                                current = q[field] <= val
                            elif op == "$eq":
                                current = q[field] == val
                            elif op == "$ne":
                                current = ~(q[field] == val)
                            elif op == "$in":
                                if not isinstance(val, list):
                                    raise ValueError("$in 操作符要求值为列表")
                                # 使用 test 方法构造 in 查询
                                current = q[field].test(lambda v, lst=val: v in lst)
                            elif op == "$nin":
                                if not isinstance(val, list):
                                    raise ValueError("$nin 操作符要求值为列表")
                                current = ~(q[field].test(lambda v, lst=val: v in lst))
                            elif op == "$exists":
                                # 若 val 为 True，则判断字段值不为 None；若为 False，则判断为 None
                                current = (q[field] is not None) if val else (q[field] is None)
                            else:
                                raise ValueError(f"不支持的操作符: {op}")
                            if field_expr is None:
                                field_expr = current
                            else:
                                field_expr = field_expr & current
                        sub_exprs.append(field_expr)
                    else:
                        # 直接进行等值判断
                        sub_exprs.append(q[field] == condition)
                if not sub_exprs:
                    return None
                expr = sub_exprs[0]
                for e in sub_exprs[1:]:
                    expr = expr & e
                return expr
        else:
            raise ValueError("Mongo 查询条件必须为字典类型")

    def select(self, query: dict = None):
        """
        查询接口，接收 MongoDB 查询语法。

        示例：
            query = {"age": {"$gt": 30}, "$or": [{"name": "Alice"}, {"name": "Bob"}]}
            results = db.select(query)
        """
        if query is None or not query:
            return self.table.all()
        query_obj = self._build_query_mongo(query)
        return self.table.search(query_obj)

    def update(self, update_data: dict, query: dict = None):
        """
        更新符合 MongoDB 查询条件的记录。

        Args:
            update_data: 一个字典，指定要更新的字段和值。
            query: MongoDB 查询语法的字典，用于选择需要更新的记录。
                   如果 query 为 None 或空字典，则更新所有记录。

        Returns:
            update_result: 通常为更新的记录标识列表。
        """
        if query is None or not query:
            # 若没有指定查询条件，则更新所有记录
            return self.table.update(update_data)
        query_obj = self._build_query_mongo(query)
        return self.table.update(update_data, query_obj)

    def delete(self, query: dict = None):
        """
        删除符合 MongoDB 查询条件的记录。

        Args:
            query: MongoDB 查询语法的字典，用于选择需要删除的记录。
                   如果 query 为 None 或空字典，则删除所有记录。

        Returns:
            delete_result: 通常为删除的记录标识列表。
        """
        if query is None or not query:
            # 若没有指定查询条件，则删除所有记录
            return self.table.remove()
        query_obj = self._build_query_mongo(query)
        return self.table.remove(query_obj)
