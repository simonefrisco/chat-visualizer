
import os



def update_chat_history(session_id, log_messages):
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