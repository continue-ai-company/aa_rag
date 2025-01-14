from aa_rag.gtypes.enums import IndexType, EmbeddingModel, DBMode, RetrieveType

# vector db path
INDEX_VECTOR_DB_PATH = "./lancedb"
# index type
INDEX_TYPE = IndexType.CHUNK
# chunk size
INDEX_CHUNK_SIZE = 256
# chunk overlap
INDEX_OVERLAP_SIZE = 100
# db mode
INDEX_DB_MODE = DBMode.DEINSERT

# embedding model
EMBEDDING_MODEL = EmbeddingModel.TEXT_EMBEDDING_3_SMALL



# retrieve type
RETRIEVE_TYPE = RetrieveType.HYBRID
# retrieve top k
RETRIEVE_TOP_K = 3
#  hybrid retrieve weight
RETRIEVE_HYBRID_DENSE_WEIGHT = 0.5
RETRIEVE_HYBRID_SPARSE_WEIGHT = 0.5
# retrieve return only page content
RETRIEVE_ONLY_PAGE_CONTENT = False
