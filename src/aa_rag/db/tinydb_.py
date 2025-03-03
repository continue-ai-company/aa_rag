from pathlib import Path

from tinydb import TinyDB, Query
from tinydb.table import Table

from aa_rag import setting
from aa_rag.db.base import BaseNoSQLDataBase, singleton
from aa_rag.gtypes.enums import NoSQLDBType


@singleton
class TinyDBDataBase(BaseNoSQLDataBase):
    table: Table | None = None
    _db_type = NoSQLDBType.TINYDB

    def __init__(self, uri: str = setting.storage.tinydb.uri, **kwargs):
        self.uri = uri
        # create parent directory if not exist
        Path(self.uri).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(**kwargs)

    @property
    def connection(self) -> TinyDB:
        return self._conn_obj

    def connect(self):
        return TinyDB(self.uri)

    def create_table(self, table_name, **kwargs):
        return self.connection.table(table_name, **kwargs)

    def using(self, table_name, **kwargs):
        """
        get table object by table name, return self for with statement.
        """
        self.table = self.connection.table(table_name, **kwargs)
        return self

    def table_list(self):
        """
        return all table names in the database.
        """
        return self.connection.tables()

    def drop_table(self, table_name):
        """
        drop table by table name.
        """
        return self.connection.drop_table(table_name)

    def insert(self, data):
        """
        insert data into table.
        """
        return self.table.insert(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.table = None
        return False

    def close(self):
        self.connection.close()

    def _build_query_mongo(self, mongo_query: dict, q: Query = None):
        """
        Convert MongoDB query syntax to TinyDB query expressions.

        Supported MongoDB query operators include:
          - Comparison operators: $gt, $gte, $lt, $lte, $eq, $ne
          - Collection operators: $in, $nin
          - Existence judgment: $exists
          - Logical operators: $and, $or, $nor, $not

        Example:
          {"age": {"$gt": 30, "$lt": 50}, "name": "John"}
          Equivalent to:
          (Query()['age'] > 30) & (Query()['age'] < 50) & (Query()['name'] == "John")
        """
        if q is None:
            q = Query()
        if isinstance(mongo_query, dict):
            # handle top-level logical operators
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
                # handle field-level operators
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
                                    raise ValueError("$in requires a list value")
                                # use the test method to construct in query
                                current = q[field].test(lambda v, lst=val: v in lst)
                            elif op == "$nin":
                                if not isinstance(val, list):
                                    raise ValueError("$nin requires a list value")
                                current = ~(q[field].test(lambda v, lst=val: v in lst))
                            elif op == "$exists":
                                # check the field is None if val is False, otherwise check it is not None
                                current = (
                                    (q[field] is not None)
                                    if val
                                    else (q[field] is None)
                                )
                            else:
                                raise ValueError(f"Unsupported Operation: {op}")
                            if field_expr is None:
                                field_expr = current
                            else:
                                field_expr = field_expr & current
                        sub_exprs.append(field_expr)
                    else:
                        # make a direct judgment of equal value
                        sub_exprs.append(q[field] == condition)
                if not sub_exprs:
                    return None
                expr = sub_exprs[0]
                for e in sub_exprs[1:]:
                    expr = expr & e
                return expr
        else:
            raise ValueError("Mongo Query Condition Must Be A Dict")

    def select(self, query: dict = None):
        """
        Query the interface and receive MongoDB query syntax.
        Args:
            query: A dict representing the MongoDB query.

        Example:
            query = {"age": {"$gt": 30}, "$or": [{"name": "Alice"}, {"name": "Bob"}]}
            results = db.select(query)
        """
        if query is None or not query:
            return self.table.all()
        query_obj = self._build_query_mongo(query)
        return self.table.search(query_obj)

    def update(self, update_data: dict, query: dict = None):
        """
        Update records that meet MongoDB query criteria.

        Args:
            update_data: A dictionary that specifies the fields and values to be updated.
            query: MongoDB dictionary of query syntax, used to select records that need to be updated.
                   If query is None or an empty dictionary, all records are updated.

        Returns:
            update_result: Usually an updated record identification list.
        """
        if query is None or not query:
            # If no query conditions are specified, all records will be updated.
            return self.table.update(update_data)
        query_obj = self._build_query_mongo(query)
        return self.table.update(update_data, query_obj)

    def delete(self, query: dict = None):
        """
        Delete records that meet MongoDB query criteria.

        Args:
            query: MongoDB dictionary of query syntax, used to select records to be deleted.
                   If query is None or an empty dictionary, all records are deleted.

        Returns:
            delete_result: Usually a list of deleted records.
        """
        if query is None or not query:
            # If no query conditions are specified, all records will be deleted.
            return self.table.remove()
        query_obj = self._build_query_mongo(query)
        return self.table.remove(query_obj)
