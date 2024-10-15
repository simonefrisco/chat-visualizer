import lancedb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import pyarrow as pa
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_core.documents import Document
import tiktoken

EMBEDDING_MODEL = os.environ['EMBEDDING_MODEL']
LANCE_PATH      = os.environ['LANCE_PATH']
TABLE_NAME      = os.environ['TABLE_NAME']

db    = lancedb.connect(LANCE_PATH)

def token_count(text : str = None , model : str = "gpt-3.5-turbo"):
    return len(tiktoken.encoding_for_model(model).encode(text))

def get_docs(table_name : str):
    table = db.open_table(table_name)
    return table.to_pandas()