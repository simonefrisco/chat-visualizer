"""
- LanceDb Default API
"""
import lancedb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from pathlib import Path
import os
from dotenv import load_dotenv
import asyncio
import pyarrow as pa
import boto3
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_core.documents import Document

BUCKET          = os.environ['BUCKET']
EMBEDDING_MODEL = os.environ['EMBEDDING_MODEL']
LANCE_PATH      = os.environ['LANCE_PATH']
TABLE_NAME      =  os.environ['TABLE_NAME']

db    = lancedb.connect(LANCE_PATH)
model = get_registry()\
            .get("sentence-transformers")\
            .create(name=EMBEDDING_MODEL, device="cpu")

class Wiki(LanceModel):
     text : str = model.SourceField()
     vector: Vector(model.ndims()) = model.VectorField()
     file_name : str
     start_index : int
     id : int

try :
    print('Creating table')
    table = db.create_table(TABLE_NAME, schema=Wiki)
except Exception as e:
    print('Error creating table : ', e)
    print('Table already exists, opening it..')
    table = db.open_table(TABLE_NAME)

def add_doc_to_lance_table (name : str = None , text : str = None):

    small_chunk_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_000 , chunk_overlap = 100, add_start_index=True
    )
    tmp_doc = [Document(
    page_content=text,
    metadata={"source": name}
    )]
    chunks = []
    for doc_path in path_doc_list:
        tmp_splitted_docs = small_chunk_splitter.split_documents(tmp_doc)
        chunks.extend(tmp_splitted_docs)

    docs = [{
            "text" : i.page_content ,
            "id" : k ,
            "file_name"  : i.metadata['source'] , 
            "start_index": i.metadata['start_index']
        } for k, i in enumerate(chunks)]

    table.add(docs)
    table.create_fts_index("text", use_tantivy=False)
    print('Document uploaded')