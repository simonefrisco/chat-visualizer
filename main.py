import marimo

__generated_with = "0.9.4"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    from dotenv import load_dotenv
    load_dotenv('.dev.env')
    return


@app.cell
def __(os):
    BUCKET = os.environ['BUCKET']
    TABLE_VERSION = "mr_wiki"
    SESSION_ID = '106'
    return BUCKET, SESSION_ID, TABLE_VERSION


@app.cell
def __(handler, mo):
    chat = mo.ui.chat(handler)
    return (chat,)


@app.cell
def __(chat):
    chat
    return


@app.cell
def __(chat):
    chat.value
    return


@app.cell
def __(mo):
    get_messages, set_messages = mo.state([])
    return get_messages, set_messages


@app.cell
def __(
    ChatMessage,
    List,
    SESSION_ID,
    client,
    get_message_system,
    logger,
    rephrase_user_message,
    retrieve_context,
    time,
    update_chat_history,
):
    def handler(current_messages : List[ChatMessage], config):
        user_message = current_messages.pop(-1)
        history      = current_messages

        # DYNAMODB_TABLE = "MQSessionTableDev"
        # CHAT_MODEL = "llama-3.2-3b-preview"
        CHAT_MODEL = "mixtral-8x7b-32768"
        rephrased_user_message, rephrase_ts_exec = None, None
        #* ====== Init Chat Session ==========================
        if len(history) == 0:
            log_messages = [get_message_system('context_placeholder')]
            logger.info("Initializing new chat session")
            retrieve_start_time = time.time()
            context, chunk_ids, source_docs = retrieve_context(user_message.content, None)
            retrieve_ts_exec = time.time() - retrieve_start_time
            message_system = get_message_system(context)
            messages = [message_system, {"role": user_message.role, "content": user_message.content}]

        #* ====== Fetch Chat Session ==========================
        else:      
            log_messages = []
            logger.info("Fetching existing chat session")
            rephrased_user_message, rephrase_ts_exec = rephrase_user_message(history, user_message.content)

            retrieve_start_time = time.time()
            context, chunk_ids, source_docs = retrieve_context(rephrased_user_message, None)
            retrieve_ts_exec = time.time() - retrieve_start_time

            message_system = get_message_system(context)
            messages = [message_system] +  [ {"role": item.role, "content": item.content.replace('\n', ' ')} for item in history ] + [{"role": "user", "content": rephrased_user_message}]


        # Call GROQ API
        logger.info("Calling GROQ API")
        response_ts_start = time.time()
        response = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
        response_ts_exec = time.time() - response_ts_start

        assistant_reply = response.model_dump()["choices"][0]["message"]["content"]
        logger.debug(f"Assistant reply: {assistant_reply}")

        log_messages.extend([{
            "role": "user",
            "content": user_message.content,
            "contextualize_message": rephrased_user_message,
            "retrieve_ts_exec": retrieve_ts_exec,
            "rephrase_ts_exec": rephrase_ts_exec,
            "chunk_ids": chunk_ids,
            "source_docs": source_docs
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
        return assistant_reply
    return (handler,)


@app.cell
def __(json):
    def update_chat_history(session_id, log_messages):
                # Load existing chat history from JSON file
        history_file = f"data/experiments/chat_history_{session_id}.json"
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
    return (update_chat_history,)



@app.cell
def __(__file__):
    import json
    import os
    from loguru import logger
    import time
    from pathlib import Path
    import sys
    import os
    sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent))
    print(Path(os.path.dirname(os.path.abspath(__file__))).parent)
    from lambdas.lambda_02_chat_local.app_mr import retrieve_context, get_message_system, client, vector_table,rephrase_user_message
    return (
        Path,
        client,
        get_message_system,
        json,
        logger,
        os,
        rephrase_user_message,
        retrieve_context,
        sys,
        time,
        vector_table,
    )


if __name__ == "__main__":
    app.run()