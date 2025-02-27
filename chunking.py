from chonkie import SemanticChunker
from chonkie import SDPMChunker

# Basic initialization with default parameters
# chunker = SemanticChunker(
chunker = SDPMChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # Default model
    threshold=0.5,                               # Similarity threshold (0-1) or (1-100) or "auto"
    chunk_size=512,                              # Maximum tokens per chunk
    min_sentences=1,                  # Initial sentences per chunk
    skip_window=1
)


with open("transcript.txt", "r") as file:
    transcript = file.read()

chunks = chunker.chunk(transcript)

for chunk in chunks:
    print(f"Chunk text: {chunk.text}")
    print(f"Token count: {chunk.token_count}")
    print(f"Number of sentences: {len(chunk.sentences)}")
