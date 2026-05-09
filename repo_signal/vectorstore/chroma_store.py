from pathlib import Path
import math
import re
from typing import List, Optional

from repo_signal.vectorstore.chunks import SymbolChunk


DEFAULT_COLLECTION = "symbols"
DEFAULT_DIMENSIONS = 96
DEFAULT_VECTORSTORE_ROOT = Path("~/.repo-signal/vectorstores")


class ChromaUnavailableError(RuntimeError):
    """Raised when chromadb is not installed."""


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_:-]+", text.lower())


def local_embedding(text: str, dimensions: int = DEFAULT_DIMENSIONS) -> List[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        index = hash(token) % dimensions
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        return vector
    return [value / norm for value in vector]


class ChromaSymbolStore:
    def __init__(
        self,
        path: Path,
        collection_name: str = DEFAULT_COLLECTION,
    ) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise ChromaUnavailableError(
                "chromadb is not installed. Install with `pip install chromadb` or use lexical semantic search."
            ) from exc

        self.client = chromadb.PersistentClient(path=str(path))
        self.path = path
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def upsert_chunks(self, chunks: List[SymbolChunk]) -> int:
        if not chunks:
            return 0

        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=[local_embedding(chunk.text) for chunk in chunks],
        )
        return len(chunks)

    def query(self, query_text: str, limit: int = 5) -> List[dict]:
        result = self.collection.query(
            query_embeddings=[local_embedding(query_text)],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for index, item_id in enumerate(ids):
            matches.append(
                {
                    "id": item_id,
                    "text": documents[index],
                    "metadata": metadatas[index],
                    "distance": distances[index],
                }
            )

        return matches


def safe_repo_store_name(repo_path: Path) -> str:
    name = repo_path.expanduser().resolve().name
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", name).strip("-") or "repository"


def default_vectorstore_root() -> Path:
    return DEFAULT_VECTORSTORE_ROOT.expanduser()


def default_repo_store_path(repo_path: Path, root: Optional[Path] = None) -> Path:
    base = root.expanduser() if root else default_vectorstore_root()
    return base / safe_repo_store_name(repo_path)


def build_default_store(repo_path: Path, store_path: Optional[Path] = None) -> ChromaSymbolStore:
    path = store_path.expanduser() if store_path else default_repo_store_path(repo_path)
    path.mkdir(parents=True, exist_ok=True)
    return ChromaSymbolStore(path=path, collection_name=DEFAULT_COLLECTION)
