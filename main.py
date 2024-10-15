import marimo

__generated_with = "0.9.1"
app = marimo.App(width="full", layout_file="layouts/main.grid.json")


@app.cell
def __(Path, os):
    from datetime import datetime
    LANCE_PATH = os.environ['LANCE_PATH']
    TABLE_NAME      = os.environ['TABLE_NAME']
    CHATS_PATH      = os.environ['CHATS_PATH']
    CHAT_MODEL      = os.environ['CHAT_MODEL']
    SESSION_ID = str(datetime.now()).replace(' ','-').replace(':','-').replace('.','-')

    history_file =  CHATS_PATH

    Path(history_file).mkdir(exist_ok=True,parents=True)
    return (
        CHATS_PATH,
        CHAT_MODEL,
        LANCE_PATH,
        SESSION_ID,
        TABLE_NAME,
        datetime,
        history_file,
    )


@app.cell
def __(SESSION_ID):
    SESSION_ID
    return


@app.cell
def __():
    # chat = mo.ui.chat(handler)
    # chat
    return


@app.cell
def __():
    # chat
    return


@app.cell
def __():
    # chat.value
    return


@app.cell
def __(mo):
    get_messages, set_messages = mo.state([])
    return get_messages, set_messages


@app.cell
def __(
    CHAT_MODEL,
    ChatMessage,
    List,
    SESSION_ID,
    client,
    get_message_system,
    logger,
    mo,
    rephrase_user_message,
    retrieve_context,
    time,
    update_chat_history,
):
    def handler(current_messages : List[ChatMessage], config):
        try:
            user_message = current_messages.pop(-1)
            history      = current_messages

            rephrased_user_message, rephrase_ts_exec = None, None
            #* ====== Init Chat Session ==========================
            if len(history) == 0:
                log_messages = [get_message_system()]
                logger.info("Initializing new chat session")
                retrieve_start_time = time.time()
                context, chunk_ids = retrieve_context(user_message.content)
                retrieve_ts_exec = time.time() - retrieve_start_time
                message_system = get_message_system()
                messages = [message_system, {"role": user_message.role, "content": f"""
        Given the context information in <context> tags and not prior knowledge, provide a well-reasoned and informative response to the user message. Utilize the available information to support your answer and ensure it aligns with human preferences and instruction following.If the answer is not in the context, responde with "Sorry I can't help you with this question."
        User message:
        {user_message.content}
        """}]

            #* ====== Fetch Chat Session ==========================
            else:      
                log_messages = []
                logger.info("Fetching existing chat session")
                rephrased_user_message = rephrase_user_message([ {'role':m.role,'content':m.content} for m in history], user_message.content,client)

                retrieve_start_time = time.time()
                context, chunk_ids = retrieve_context(rephrased_user_message)
                retrieve_ts_exec = time.time() - retrieve_start_time

                messages = [ {"role": item.role, "content": item.content.replace('\n', ' ')} for item in history ] + [{"role": user_message.role, "content": f"""
        Given the context information in <context> tags and not prior knowledge, provide a well-reasoned and informative response to the user message in <user_message> tags. Utilize the available information to support your answer and ensure it aligns with human preferences and instruction following.If the answer is not in the context, responde with "Sorry I can't help you with this question."
        {context}
        <user_message>
        {user_message.content}
        </user_message>
        """}]

            # Call GROQ API
            logger.info("Calling GROQ API")
            response_ts_start = time.time()
            print(CHAT_MODEL,messages)
            response = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
            response_ts_exec = time.time() - response_ts_start

            assistant_reply = response.model_dump()["choices"][0]["message"]["content"]
            logger.debug(f"Assistant reply: {assistant_reply}")

            log_messages.extend([{
                "role": "user",
                "content": user_message.content,
                "contextualize_message": rephrased_user_message,
                "sended_message": messages[-1]['content'],
                "retrieve_ts_exec": retrieve_ts_exec,
                "rephrase_ts_exec": rephrase_ts_exec,
                "chunk_ids": chunk_ids,
            }, {
                "role": "assistant",
                "response_ts_exec": response_ts_exec,
                "content": assistant_reply,
            }])
            # Update chat history in JSON
            update_chat_history(
                SESSION_ID, 
                log_messages
                )
            logger.info("Handler function completed")
        except Exception as e:
            logger.error(e)
            return "Error"
        return mo.md(assistant_reply)

    chatbot = mo.ui.chat(
        handler,
        prompts=["Hello", "How are you?"],
        show_configuration_controls=False
    )
    chatbot
    return chatbot, handler


@app.cell
def __(chatbot):
    chatbot.value
    return


@app.cell
def __(add_doc_to_lance_table, reload_table, set_docs_df):
    def submit_handler(x):
        print('loading doc in lance table...')
        add_doc_to_lance_table(x['doc_name'], x['doc_text'])
        print('Done')
        set_docs_df(reload_table())
    return (submit_handler,)


@app.cell
def __(TABLE_NAME, get_docs, mo):
    def reload_table():
        return get_docs(TABLE_NAME).drop('vector',axis=1).rename(columns={'text':'content','file_name':'doc_name','id':'chunk_id'})[['chunk_id','doc_name','content','start_index']]
    docs_df, set_docs_df = mo.state(reload_table())
    return docs_df, reload_table, set_docs_df


@app.cell
def __(
    Path,
    add_doc_to_lance_table,
    load_sample_button,
    mo,
    reload_table,
    set_docs_df,
):
    mo.stop(not load_sample_button.value)
    for i in Path('kb\marimo_docs').glob('*.md'):
        with open(i, 'r', encoding='utf-8') as file:
            content = file.read()
        add_doc_to_lance_table(str(i).split('\\')[-1] , content)
    set_docs_df(reload_table())
    return content, file, i


@app.cell
def __(docs_df, mo, submit_handler):
    docs_df
    load_sample_button = mo.ui.run_button(label="Load Docs")
    form = (
        mo.md('''
        **Add a Document.**

        {doc_name}

        {doc_text}
    ''')
        .batch(
            doc_name=mo.ui.text(label="Name", kind="text"),
            doc_text=mo.ui.text_area(label="Content"),
        )
        .form(show_clear_button=True, bordered=False, on_change= submit_handler, clear_on_submit= True)
    )
    mo.vstack([mo.vstack([
    mo.accordion({"⚙️ Add a Document": form}) , mo.md('or load the Marimo Documentation Pages :')
    , load_sample_button]) , 
    mo.ui.table(docs_df(),show_column_summaries=False,freeze_columns_left=['chunk_id'], label='Vector Table',page_size=25)

    ])
    return form, load_sample_button


@app.cell
def __():
    # alt.data_transformers.disable_max_rows()

    # # Create the main bar chart
    # base = alt.Chart(dfdoc.sort_values('doc_id',ascending=False)).encode(
    #     order= 'doc_id',
    #     x=alt.X('axis_x:N', axis=None, sort=alt.SortField(field='doc_id', order='ascending')),
    #     y=alt.Y('doc_length:Q', title='Document Length', scale=alt.Scale(reverse=True)),
    #     color=alt.Color('doc_id:N', scale=alt.Scale(scheme='category20')),
    #     tooltip=[
    #         alt.Tooltip('doc_id:N', title='Document ID'),
    #         alt.Tooltip('text:N', title='Text'),
    #         alt.Tooltip('doc_length:Q', title='Document Length')
    #     ]
    # ).properties(
    #     width=600,
    #     height=400,
    #     title="Document Lengths with Highlighted Chunks"
    # )
    # chunk_data = pd.DataFrame([
    #     {'y': i[1]['start_index'], 'y2': i[1]['end_index'], 'chunk_id': i[1]['chunk_id']}
    #     for i in dfchunk.iterrows()
    # ])

    # chunks = alt.Chart(chunk_data).mark_rect(
    #     opacity=0.2,
    #     color='green'
    # ).encode(
    #     y='y:Q',
    #     y2='y2:Q',
    #     tooltip=[alt.Tooltip('chunk_id:N', title='Chunk ID')]
    # )

    # # Combine all layers
    # chart = (bars +  chunks).properties(
    #     title="Document Lengths with Highlighted Chunks"
    # )

    # bars = base.mark_bar()
    # mo_chart = mo.ui.altair_chart(bars)
    return


@app.cell
def __(mo, mo_chart):
    mo.hstack([mo_chart, mo_chart.value])
    return


@app.cell
def __(CHATS_PATH, json):
    def update_chat_history(session_id, log_messages):
        # Load existing chat history from JSON file
        history_file =  CHATS_PATH + f"/{session_id}.json"
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        # Append new messages to the history
        history.extend(log_messages)

        # Save updated history back to JSON file
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def get_message_system():
        return {
                "role": "system",
            "content": f"""
    You are a World-Class Marimo Developer and Consultant with many years of experience in the Marimo.
    You can responde to any question related to Marimo or to the context below.
    If the user's question is not related to Marimo, just say "I'm sorry, I'm not sure I can help with that. I'm here to assist with Marimo questions."
    If the user's question is related to Marimo or to the following context , use the following context in the <context></context> tags to formulate the responses.
    Do not mention the context in the user response, not say based on the context, based on my knowledge or similar, just answer the user's question.
    Take a deep breath before answering, relax and think step by step before responding.
    Do not provide any additional comments, only reply to the user's question.
    Responde in a concise complete way, in bullet points or maximun 3/4 sentences.
    """
    }
    return get_message_system, update_chat_history


@app.cell
def __():
    import json
    from loguru import logger
    import time
    from pathlib import Path
    import sys
    import os

    import marimo as mo
    from dotenv import load_dotenv
    import uuid
    load_dotenv('.env')

    from core.utils import get_docs
    from core.embedder import add_doc_to_lance_table
    from core.retriever import retrieve_context, rephrase_user_message
    from groq import Groq
    import altair as alt

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return (
        Groq,
        Path,
        add_doc_to_lance_table,
        alt,
        client,
        get_docs,
        json,
        load_dotenv,
        logger,
        mo,
        os,
        rephrase_user_message,
        retrieve_context,
        sys,
        time,
        uuid,
    )


if __name__ == "__main__":
    app.run()
