import marimo

__generated_with = "0.9.12"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __():
    def get_segment_boundaries(chunks):
        """
        Break chunks into non-overlapping segments while tracking which chunks cover each segment.

        Args:
            chunks (list): List of chunk dictionaries with start and end indices

        Returns:
            list: List of segments with start, end, and associated chunk IDs
        """
        # Collect all unique positions where chunks start or end
        boundaries = set()
        for chunk in chunks:
            boundaries.add(chunk['chunkStartIndex'])
            boundaries.add(chunk['chunkEndIndex'])
        boundaries = sorted(list(boundaries))

        # Create segments between each pair of consecutive boundaries
        segments = []
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            # Find all chunks that cover this segment
            covering_chunks = []
            for chunk in chunks:
                if chunk['chunkStartIndex'] <= start and chunk['chunkEndIndex'] >= end:
                    covering_chunks.append(chunk['chunkId'])
            if covering_chunks:  # Only add segment if it's covered by at least one chunk
                segments.append({
                    'start': start,
                    'end': end,
                    'chunk_ids': covering_chunks
                })

        return segments

    def get_highlight_style(chunk_ids, highlight_colors):
        """
        Generate CSS style for a segment based on which chunks cover it.

        Args:
            chunk_ids (list): List of chunk IDs covering this segment
            highlight_colors (dict): Mapping of chunk IDs to colors

        Returns:
            str: CSS style string
        """
        if len(chunk_ids) == 1:
            # Single chunk - use solid background
            return f"background-color: {highlight_colors[chunk_ids[0]]};"
        else:
            # Multiple chunks - create diagonal stripes
            colors = [highlight_colors[chunk_id] for chunk_id in chunk_ids]
            stripe_width = 100 // len(colors)  # Width of each stripe in pixels
            gradients = []
            for i, color in enumerate(colors):
                start = i * stripe_width
                end = (i + 1) * stripe_width
                gradients.append(f"{color} {start}px, {color} {end}px")

            return (
                f"background: repeating-linear-gradient("
                f"45deg, {', '.join(gradients)});"
                f"background-size: {len(colors) * stripe_width}px {len(colors) * stripe_width}px;"
            )

    def highlight_document_chunks(doc_name, docs, chunks):
        """
        Highlight chunks within a document, handling overlapping chunks with different visual styles.

        Args:
            doc_name (str): Name of the document to process
            docs (list): List of document dictionaries with 'name' and 'content' keys
            chunks (list): List of chunk dictionaries with 'docName', 'chunkStartIndex', 'chunkEndIndex'

        Returns:
            str: HTML formatted string with highlighted chunks
        """
        # Define colors for chunks
        base_colors = {
            1: "#FFD700",  # Gold
            2: "#98FB98",  # Pale Green
            3: "#87CEFA",  # Light Sky Blue
            4: "#DDA0DD",  # Plum
            5: "#F08080",  # Light Coral
            6: "#E0FFFF",  # Light Cyan
        }

        # Find the document
        doc = next((d for d in docs if d['name'] == doc_name), None)
        if not doc:
            return f"Document '{doc_name}' not found."

        # Get chunks for this document
        doc_chunks = [c for c in chunks if c['docName'] == doc_name]
        if not doc_chunks:
            return f"No chunks found for document '{doc_name}'\n\n{doc['content']}"

        # Get non-overlapping segments with their associated chunks
        segments = get_segment_boundaries(doc_chunks)

        # Build the output HTML
        html = f"<h2>Document: {doc_name}</h2>\n\n<p>"
        current_pos = 0
        content = doc['content']

        # Process each segment
        for segment in segments:
            # Add text before segment
            html += content[current_pos:segment['start']]

            # Create style for this segment based on covering chunks
            style = get_highlight_style(segment['chunk_ids'], base_colors)

            # Add the segment text with appropriate styling
            chunk_labels = ', '.join([str(chunk_id) for chunk_id in segment['chunk_ids']])
            html += (
                f'<span style="{style} padding: 2px 4px; border-radius: 4px;" '
                f'title="Chunks: {chunk_labels}">'
                f'{content[segment["start"]:segment["end"]]}'
                f'</span>'
            )

            current_pos = segment['end']

        # Add remaining text
        html += content[current_pos:]
        html += "</p>"

        # Add legend
        html += "\n\n<h3>Chunk Legend:</h3>\n"
        for chunk in doc_chunks:
            chunk_id = chunk['chunkId']
            color = base_colors[chunk_id]
            html += (
                f'<div style="margin: 5px 0;">'
                f'<span style="background-color: {color}; padding: 2px 4px; '
                f'border-radius: 4px;">Chunk {chunk_id}: positions {chunk["chunkStartIndex"]}-{chunk["chunkEndIndex"]}'
                f'</span></div>\n'
            )

        return html
    return (
        get_highlight_style,
        get_segment_boundaries,
        highlight_document_chunks,
    )


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
        {"docName": "doc1", "chunkId": 2, "chunkStartIndex": 20, "chunkEndIndex": 40},
        {"docName": "doc1", "chunkId": 3, "chunkStartIndex": 30, "chunkEndIndex": 60},
        {"docName": "doc1", "chunkId": 3, "chunkStartIndex": 45, "chunkEndIndex": 70},
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
                add_start_index = True, strip_whitespace=True
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
