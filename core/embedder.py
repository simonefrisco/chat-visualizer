"""
- LanceDb Default API
"""
import lancedb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_core.documents import Document
from core.utils import token_count

EMBEDDING_MODEL = os.environ['EMBEDDING_MODEL']
LANCE_PATH      = os.environ['LANCE_PATH']
TABLE_NAME      = os.environ['TABLE_NAME']

db    = lancedb.connect(LANCE_PATH)
model = get_registry()\
            .get("sentence-transformers")\
            .create(name=EMBEDDING_MODEL, device="cpu")

class Wiki(LanceModel):
     text : str = model.SourceField()
     vector: Vector(model.ndims()) = model.VectorField()
     file_name : str
     start_index : int
     start_token_index : int
     doc_token_count : int
     start_index_len : int
     chunk_len : int
     doc_len : int
     id : int

try :
    print('Creating table')
    db.create_table(TABLE_NAME, schema=Wiki)
except Exception as e:
    print('Error creating table : ', e)
    print('Table already exists, opening it..')
    db.open_table(TABLE_NAME)
    
def add_doc_to_lance_table (name : str = None , text : str = None):
    table_ = db.open_table(TABLE_NAME)
    small_chunk_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_000 , chunk_overlap = 0, add_start_index=True
    )
    try:
        last_id = int(table_.to_pandas()['id'].max())
    except:
        last_id = 0
    tmp_doc = [Document(
    page_content=text,
    metadata={"source": name}
    )]
    tmp_splitted_docs = small_chunk_splitter.split_documents(tmp_doc)
    docs = []
    doc_token_count = token_count(text)
    running_doc = ""
    for k, i in enumerate(tmp_splitted_docs):
        docs.append({
            "text" : i.page_content ,
            "id" : k + last_id + 1,
            "file_name"  : i.metadata['source'] ,
            "start_index": i.metadata['start_index'],
            "start_index_len": len(running_doc),
            "chunk_len": len( i.page_content),
            "start_token_index": token_count(running_doc),
            "doc_token_count" : doc_token_count,
            "doc_len" : len(text)
        })
        running_doc = running_doc + i.page_content 

    table_.add(docs)
    table_.create_fts_index("text", use_tantivy=False,replace=True)
    print('Document uploaded')