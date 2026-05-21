# Semantic Memory Upload

`semantic-upload` builds a compact symbol map of the repository and uploads it
to an OpenAI vector store, making it available to `ask` for higher-quality
answers.

## Generation flow

```text
Repository.load(".")
→ build_openai_memory_document()
→ {repo-name}-symbol-memory.md
→ OpenAI vector store
```

## Usage

```bash
# dry-run: build the document without uploading
repo-signal semantic-upload --dry-run

# upload to vector store configured by OPENAI_VECTOR_STORE_ID
repo-signal semantic-upload

# include test symbols
repo-signal semantic-upload --include-tests

# target a specific store
repo-signal semantic-upload --vector-store-id vs_abc123
```

## Configuration

Configure the target store:

```bash
export OPENAI_VECTOR_STORE_ID="vs_abc123"
```

Verify the upload worked:

```bash
repo-signal ask "which files implement semantic-upload?"
```
