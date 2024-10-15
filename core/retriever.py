import json
import os
from typing import Any, Callable, Tuple
import time
from loguru import logger
import lancedb
from groq import Groq
import polars as pl

EMBEDDING_MODEL = os.environ['EMBEDDING_MODEL']
LANCE_PATH      = os.environ['LANCE_PATH']
TABLE_NAME      = os.environ['TABLE_NAME']
CHAT_MODEL      = os.environ['CHAT_MODEL']

db    = lancedb.connect(LANCE_PATH)
table = db.open_table(TABLE_NAME)

def retrieve_context(query):
    similar_chunks = table.search(query).limit(5).to_list()
    similar_chunks_df = pl.DataFrame(similar_chunks)
    logger.debug(similar_chunks_df)

    chunk_ids = []
    context="<context>"
    for c in similar_chunks:
        chunk_ids.append({
            'file_name' : c["file_name"] , 
            'chunk_id' : str(c["id"]) , 
            'score': str(c["_distance"])[:5]
        })
        context += f"""<chunk file_name='{c["file_name"]}' id='{c["id"]}' > {c["text"] }</chunk>\n"""
    context += "</context>"
    return context.strip(), chunk_ids

def rephrase_user_message(history, user_message,client):
    formatted_history = [ item["content"].replace('\n', ' ') for item in history ]
    formatted_history = ";".join([f"""<message role: '{item["role"]}'>\n{item["content"]}\n</message>""" for item in history ])
    logger.debug(f"Chat History: {formatted_history}")
    pre_messages = [{"role": "system", "content": f"""
Given a chat history and the latest user question in <message> tags which might reference context in the chat history <chat_history> tags, formulate a standalone question which can be understood 
without the chat history.
Do NOT answer the question, Just reformulate it if needed and otherwise return it as is, without comment or note
<chat_history>
{formatted_history}
</chat_history>
latest user question:
<message>
{user_message}
</message>
Do NOT answer the question, Just reformulate it if needed and otherwise return it as is, without comment or note
"""}]
    pre_response                    = client.chat.completions.create(model=CHAT_MODEL, messages=pre_messages)
    pre_processed_question          = pre_response.model_dump()["choices"][0]["message"]["content"]
    logger.debug(f"pre_processed_question: {pre_processed_question}")
    return pre_processed_question