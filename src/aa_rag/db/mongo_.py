from typing import Any

from aa_rag import setting
from aa_rag.db.base import BaseNoSQLDataBase, singleton


@singleton
class MongoDBDataBase(BaseNoSQLDataBase):
    _db_type = "MongoDB"

    collection: Any

    def __init__(
        self,
        uri: str = setting.storage.mongodb.uri,
        db_name: str = setting.storage.mongodb.db_name,
        **kwargs,
    ):
        """
        Initialize the MongoDB database instance.

        Args:
            uri: MongoDB connection URI, e.g., "mongodb://localhost:27017"
            db_name: The database name to use; defaults to "default"
            **kwargs: Additional keyword arguments
        """

        super().__init__(uri=uri, db_name=db_name, **kwargs)

    def connect(self, **kwargs):
        """Establish and return a MongoDB client connection."""
        try:
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(
                "MongoDB can only be enabled on the online service, please execute `pip install aa-rag[online]`."
            )
        client = MongoClient(kwargs.get("uri"))

        return client[kwargs.get("db_name")]

    def create_table(self, collection_name: str, **kwargs):
        """
        Create and return a collection with the specified name.
        If the collection already exists, return the existing one.

        Args:
            collection_name: The name of the collection.
            **kwargs: Additional optional parameters for collection creation.

        Returns:
            The collection object.
        """
        if collection_name in self.table_list():
            return self.connection[collection_name]
        else:
            # The create_collection method will raise an exception if the collection exists,
            # so we check for its existence first.
            return self.connection.create_collection(collection_name, **kwargs)

    def using(self, collection_name: str, **kwargs):
        """
        Set the current active collection and return self to support method chaining.

        Args:
            collection_name: The name of the collection.
            **kwargs: Reserved for additional parameters.

        Returns:
            self
        """
        self.collection = self.connection[collection_name]
        return self

    def table_list(self):
        """
        Return a list of all collection names in the current database.
        """
        return self.connection.list_collection_names()

    def drop_table(self, collection_name: str):
        """
        Drop the collection with the specified name.

        Args:
            collection_name: The name of the collection.

        Returns:
            The result of the drop operation.
        """
        return self.connection.drop_collection(collection_name)

    def insert(self, data):
        """
        Insert data into the current collection.
        Supports either a single dictionary or a list of dictionaries.

        Args:
            data: A dictionary or a list of dictionaries.

        Returns:
            If a single document is inserted, returns its inserted _id;
            if multiple documents are inserted, returns a list of inserted _id's.
        """
        assert self.collection is not None, "Collection not loaded. Use using() first"

        if isinstance(data, list):
            result = self.collection.insert_many(data)
            return result.inserted_ids
        elif isinstance(data, dict):
            result = self.collection.insert_one(data)
            return result.inserted_id
        else:
            raise ValueError("Inserted data must be a dict or a list of dicts")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.collection = None
        return False

    @staticmethod
    def _build_query_mongo(mongo_query: dict) -> dict:
        """
        For MongoDB, the query condition already adheres to MongoDB's query syntax.
        Therefore, this method returns the original query (or an empty dict if None).

        Args:
            mongo_query: A dictionary representing the MongoDB query.

        Returns:
            The query dictionary.
        """
        if mongo_query is None or not mongo_query:
            return {}
        if not isinstance(mongo_query, dict):
            raise ValueError("Mongo query must be a dictionary")
        return mongo_query

    def select(self, query: dict = None):
        """
        Query the collection using MongoDB query syntax.

        Example:
            query = {"age": {"$gt": 30}, "$or": [{"name": "Alice"}, {"name": "Bob"}]}
            results = db.select(query)

        Returns:
            A list of documents matching the query.
        """
        assert self.collection is not None, "Collection not loaded. Use using() first"

        filter_query = self._build_query_mongo(query)
        # find() returns a Cursor; convert it to a list to retrieve all results.
        return list(self.collection.find(filter_query))

    def update(self, update_data: dict, query: dict = None):
        """
        Update documents in the collection that match the MongoDB query condition.

        Args:
            update_data: A dictionary specifying the fields and values to update.
                         (Internally wrapped with the $set operator.)
            query: A dictionary representing the MongoDB query.
                   If query is None or empty, all documents will be updated.

        Returns:
            The number of documents that were modified.
        """
        assert self.collection is not None, "Collection not loaded. Use using() first"

        filter_query = self._build_query_mongo(query)
        # Use the $set operator to update the fields.
        result = self.collection.update_many(filter_query, {"$set": update_data})
        return result.modified_count

    def delete(self, query: dict = None):
        """
        Delete documents in the collection that match the MongoDB query condition.

        Args:
            query: A dictionary representing the MongoDB query.
                   If query is None or empty, all documents will be deleted.

        Returns:
            The number of documents that were deleted.
        """
        assert self.collection is not None, "Collection not loaded. Use using() first"

        filter_query = self._build_query_mongo(query)
        result = self.collection.delete_many(filter_query)
        return result.deleted_count

    def close(self):
        """Close the MongoDB client connection."""
        self.connection.close()


if __name__ == "__main__":
    mongo_db = MongoDBDataBase()

    mongo_db.create_table("aarag")
    mongo_db.drop_table("aarag")

    mongo_db.create_table("fairy_tale")
    print(mongo_db.table_list())
