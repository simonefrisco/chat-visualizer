import marimo

__generated_with = "0.9.1"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __():
    def highlight_document_chunks(doc_name, docs, chunks):
        """
        Highlight chunks within a document, displaying each chunk as-is with correct boundaries.

        Args:
            doc_name (str): Name of the document to process
            docs (list): List of document dictionaries with 'name' and 'content' keys
            chunks (list): List of chunk dictionaries with 'docName', 'chunkStartIndex', 'chunkEndIndex'

        Returns:
            str: HTML formatted string with highlighted chunks
        """
        # Define colors for chunks
        base_colors = {
            1: "rgba(255, 215, 0, 0.5)",    # Gold
            2: "rgba(152, 251, 152, 0.5)",  # Pale Green
            3: "rgba(135, 206, 250, 0.5)",  # Light Sky Blue
            4: "rgba(221, 160, 221, 0.5)",  # Plum
            5: "rgba(240, 128, 128, 0.5)",  # Light Coral
            6: "rgba(224, 255, 255, 0.5)",  # Light Cyan
        }

        # Find the document
        doc = next((d for d in docs if d['name'] == doc_name), None)
        if not doc:
            return f"Document '{doc_name}' not found."

        # Get chunks for this document
        doc_chunks = [c for c in chunks if c['docName'] == doc_name]
        if not doc_chunks:
            return f"No chunks found for document '{doc_name}'\n\n{doc['content']}"

        # Build the output HTML
        html = f"<h2>Document: {doc_name}</h2>\n\n<p>"
        content = doc['content']

        # Create a list of all positions with their events (start/end)
        events = []
        for chunk in doc_chunks:
            # Add each boundary as a separate event
            events.append({
                'pos': chunk['chunkStartIndex'],
                'chunk_id': chunk['chunkId'],
                'type': 'start'
            })
            events.append({
                'pos': chunk['chunkEndIndex'],
                'chunk_id': chunk['chunkId'],
                'type': 'end'
            })

        # Sort events by position, handling overlaps
        # For same positions, process ends before starts to ensure proper nesting
        events.sort(key=lambda x: (x['pos'], 0 if x['type'] == 'end' else 1))

        # Process the document
        current_pos = 0
        active_chunks = set()  # Keep track of currently active chunks

        for event in events:
            # Add text before this position
            html += content[current_pos:event['pos']]

            if event['type'] == 'start':
                # Start of a chunk
                active_chunks.add(event['chunk_id'])
                color = base_colors[event['chunk_id']]
                html += (
                    f'<span style="background-color: {color}; '
                    f'padding: 1px 0px; border-radius: 1px;" '
                    f'title="Chunk {event["chunk_id"]}">'
                )
            else:
                # End of a chunk - close all spans up to this chunk and reopen the others
                chunk_id = event['chunk_id']
                if chunk_id in active_chunks:
                    # Close spans for this and all chunks that started after it
                    chunks_to_reopen = set()
                    while active_chunks:
                        current_chunk = max(active_chunks)  # Get most recently started chunk
                        active_chunks.remove(current_chunk)
                        html += '</span>'
                        if current_chunk != chunk_id:
                            chunks_to_reopen.add(current_chunk)
                        if current_chunk == chunk_id:
                            break

                    # Reopen spans for chunks that should continue
                    for reopen_id in sorted(chunks_to_reopen):
                        active_chunks.add(reopen_id)
                        color = base_colors[reopen_id]
                        html += (
                            f'<span style="background-color: {color}; '
                            f'padding: 1px 1px; border-radius: 1px;" '
                            f'title="Chunk {reopen_id}">'
                        )

            current_pos = event['pos']

        # Add remaining text
        html += content[current_pos:]

        # Close any remaining open spans
        for _ in active_chunks:
            html += '</span>'

        html += "</p>"

        # Add legend
        html += "\n\n<h3>Chunk Legend:</h3>\n"
        for chunk in sorted(doc_chunks, key=lambda x: x['chunkId']):
            chunk_id = chunk['chunkId']
            color = base_colors[chunk_id]
            html += (
                f'<div style="margin: 5px 0;">'
                f'<span style="background-color: {color}; padding: 2px 4px; '
                f'border-radius: 4px;">Chunk {chunk_id}: positions {chunk["chunkStartIndex"]}-{chunk["chunkEndIndex"]}'
                f'</span></div>\n'
            )

        return html
    return (highlight_document_chunks,)


@app.cell
def __(highlight_document_chunks):
    # Test with overlapping chunks
    docs = [
        {
            "name": "doc1",
            "content": "This is a sample document with some text that we want to highlight.This is a sample document with some text that we want to highlight."
        }
    ]

    chunks = [
        {"docName": "doc1", "chunkId": 1, "chunkStartIndex": 10, "chunkEndIndex": 30},
        {"docName": "doc1", "chunkId": 2, "chunkStartIndex": 30, "chunkEndIndex": 50},
        {"docName": "doc1", "chunkId": 3, "chunkStartIndex": 49, "chunkEndIndex": 70},
        {"docName": "doc1", "chunkId": 4, "chunkStartIndex": 80, "chunkEndIndex": 95},
    ]

    result = highlight_document_chunks("doc1", docs, chunks)
    print(result)
    return chunks, docs, result


@app.cell
def __(mo, result):
    mo.md(result)
    return


@app.cell
def __():
    from langchain.text_splitter import (
        CharacterTextSplitter,
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,
        MarkdownHeaderTextSplitter,
        PythonCodeTextSplitter,
        HTMLHeaderTextSplitter,
        Language,
    )
    import html

    def initialize_text_splitter(splitter_name, **kwargs):
        splitters = {
            "Character Text Splitter": CharacterTextSplitter(**kwargs),
            "Recursive Character Text Splitter": RecursiveCharacterTextSplitter(**kwargs),
            "Token Text Splitter": TokenTextSplitter(),
            "Python Code Text Splitter": PythonCodeTextSplitter(),
            "Markdown Header Text Splitter": MarkdownHeaderTextSplitter( [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]),
            "HTML Header Text Splitter": HTMLHeaderTextSplitter([
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
            ])
        }
        return splitters.get(splitter_name)
    return (
        CharacterTextSplitter,
        HTMLHeaderTextSplitter,
        Language,
        MarkdownHeaderTextSplitter,
        PythonCodeTextSplitter,
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,
        html,
        initialize_text_splitter,
    )


@app.cell
def __(mo):
    splitter_type = mo.ui.dropdown(
        label = "Select Text Splitter",
        options = [
            "Character Text Splitter",
            "Recursive Character Text Splitter",
            "Token Text Splitter",
            "Python Code Text Splitter",
            "Markdown Header Text Splitter",
            "HTML Header Text Splitter"
        ],
        value='Markdown Header Text Splitter'
    )
    # Common settings for character-based splitters
    chunk_size = mo.ui.number(
        label = "Chunk Size", 
        start=50,
        stop=2000,
        value=1000,
    )
    return chunk_size, splitter_type


@app.cell
def __(chunk_overlap, chunk_size, doc_input, splitter_type):
    splitter_type, chunk_size, chunk_overlap,doc_input
    return


@app.cell
def __(doc_input):
    doc_input.value
    return


@app.cell
def __(chunk_size, mo):
    chunk_overlap = mo.ui.number(
        label = "Chunk Overlap",
        start=0,
        stop=chunk_size.value-1,
        value=80,
    )

    # Document input
    doc_input = mo.ui.text_area(
        label = "Paste your document here",
    )
    return chunk_overlap, doc_input


@app.cell
def __(mo):
    get_chunks, set_chunks = mo.state([])
    return get_chunks, set_chunks


@app.cell
def __(
    chunk_overlap,
    chunk_size,
    doc_input,
    initialize_text_splitter,
    set_chunks,
    splitter_type,
):
    if len(doc_input.value)>0 :
        try:
            # Initialize the selected splitter with appropriate parameters
            splitter = initialize_text_splitter(
                splitter_type.value,
                chunk_size=chunk_size.value,
                chunk_overlap=chunk_overlap.value,
                add_start_index = True, 
                strip_whitespace=False
            )

            # Split the text
            set_chunks( splitter.create_documents(doc_input.value) )


        except Exception as e:
            print(f"Error processing document: {str(e)}")
            print("Note: Some splitters are designed for specific formats (e.g., Markdown, HTML, Python). Make sure you're using the appropriate splitter for your document type.")
    return (splitter,)


@app.cell
def __(get_chunks):
    get_chunks

    get_chunks()
    return


@app.cell
def __(get_chunks):
    get_chunks()[0].metadata
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
